"""Token Dashboard — macOS menu bar token usage monitor.

Displays pi-agent and opencode token usage aggregated by today / 7 days / 30 days,
grouped by model, with a bar chart popover.

Usage:
    token-dash          # as installed CLI entry point
    python token_dash.py  # direct invocation
"""

import json
from datetime import datetime, timezone

# PyObjC imports
from Foundation import NSObject, NSMakeRect
from objc import super
from WebKit import WKWebView, WKWebViewConfiguration
from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSStatusBar,
    NSVariableStatusItemLength,
    NSPopover,
    NSPopoverBehaviorTransient,
    NSTimer,
    NSViewController,
)

from .aggregator import aggregate
from .formatter import fmt
from .oc_reader import read_opencode_sessions
from .pi_reader import read_pi_agent_sessions


# ── HTML template ──────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#1c1c1e;padding:10px 14px 2px;width:300px;user-select:none}
hdr{display:flex;gap:6px;margin-bottom:8px;align-items:center}
hdr b{padding:3px 12px;border:1px solid #d1d1d6;border-radius:5px;cursor:pointer;font-size:11px;font-weight:400;color:#6e6e73;background:#fff}
hdr b.on{background:#0a84ff;border-color:#0a84ff;color:#fff}
hdr .sp{flex:1}
hdr .rf{font-size:13px;padding:3px 6px;background:transparent}

tabs{display:flex;gap:4px;margin-bottom:8px}
tabs b{flex:1;text-align:center;padding:4px 0;border:1px solid #d1d1d6;border-radius:5px;cursor:pointer;font-size:11px;font-weight:400;color:#6e6e73;background:#fff}
tabs b.on{background:#e8e8ed;border-color:#c7c7cc;color:#1c1c1e;font-weight:600}

.sec{margin-bottom:8px}
.sec .ttl{font-size:10px;color:#aeaeb2;margin-bottom:3px;text-transform:uppercase}

.mdl{margin-bottom:10px}
.mdl .mn{font-size:11px;font-weight:500;color:#1c1c1e;margin-bottom:3px}
.bar-row{display:flex;align-items:center;gap:6px;margin-bottom:2px;font-size:10px}
.bar-row .lbl{width:26px;color:#8e8e93;text-align:right;flex-shrink:0;font-size:10px}
.bar-row .fill{flex:1;height:5px;background:#e5e5ea;border-radius:3px;overflow:hidden}
.bar-row .fill-in{background:#0071e3;height:100%;border-radius:3px}
.bar-row .fill-out{background:#248b4a;height:100%;border-radius:3px}
.bar-row .fill-ca{background:#8944ab;height:100%;border-radius:3px}
.bar-row .val{width:46px;text-align:right;flex-shrink:0;font-size:10px;font-weight:500}
.in{color:#0071e3} .out{color:#248b4a} .ca{color:#8944ab}

.sum{border-top:1px solid #d1d1d6;padding-top:6px;display:flex;justify-content:space-between;font-size:11px;flex-wrap:wrap;gap:4px;margin-top:2px}
.sum .lb{color:#8e8e93}
.quit-wrap{border-top:1px solid #e5e5ea;margin-top:6px;padding-top:4px;text-align:center}
.quit-btn{width:100%;padding:2px 6px;border:none;border-radius:4px;background:transparent;color:#8e8e93;font-size:12px;cursor:pointer;display:flex;justify-content:space-between}
.quit-btn:hover{background:#f0f0f5}
.empty{color:#aeaeb2;font-size:12px;text-align:center;padding:20px 0}
</style>
</head>
<body>
<tabs>
<b id="tb-pi" class="on" onclick="swTab('pi-agent')">Pi-Agent</b>
<b id="tb-oc" onclick="swTab('opencode')">OpenCode</b>
</tabs>

<hdr>
<b id="bt-td" class="on" onclick="swRng('today')">今日</b>
<b id="bt-wk" onclick="swRng('week')">近7天</b>
<b id="bt-mo" onclick="swRng('month')">近30天</b>
<span class="sp"></span>
<b class="rf" onclick="refresh()">&#x21bb;</b>
</hdr>

<div id="ct"></div>

<script>
var D = {};
var tab = "pi-agent";
var rng = "today";

function F(n){if(!n)return"0";if(n<1000)return""+n;if(n<1e6)return(n/1000).toFixed(1)+"K";return(n/1e6).toFixed(1)+"M"}

function R(){
  var c=$("ct");
  var s = D[tab];
  if(!s){c.innerHTML='<div class="empty">暂无数据</div>';return}
  var b = s[rng];
  if(!b||!Object.keys(b.models).length){c.innerHTML='<div class="empty">该时间范围暂无数据</div>';return}
  var ta={in:0,out:0,ca:0};
  for(var k in b.models){var v=b.models[k];ta.in+=v.input;ta.out+=v.output;ta.ca+=v.cache_read}
  var h='';
  for(var k in b.models){var v=b.models[k],mt=v.input+v.output+v.cache_read;
    function lp(n){return mt?(n/mt*100):0}
    h+='<div class="mdl"><div class="mn">'+k+'</div>';
    h+='<div class="bar-row"><span class="lbl in">输入</span><span class="fill"><div class="fill-in" style="width:'+lp(v.input)+'%"></div></span><span class="val in">'+F(v.input)+'</span></div>';
    h+='<div class="bar-row"><span class="lbl out">输出</span><span class="fill"><div class="fill-out" style="width:'+lp(v.output)+'%"></div></span><span class="val out">'+F(v.output)+'</span></div>';
    h+='<div class="bar-row"><span class="lbl ca">缓存</span><span class="fill"><div class="fill-ca" style="width:'+lp(v.cache_read)+'%"></div></span><span class="val ca">'+F(v.cache_read)+'</span></div>';
    h+='<div class="bar-row"><span class="lbl" style="color:#1c1c1e;font-weight:600">总计</span><span class="fill" style="background:#e5e5ea"><div style="width:100%;height:100%;background:#8e8e93;border-radius:3px"></div></span><span class="val" style="font-weight:600;color:#1c1c1e">'+F(mt)+'</span></div>';
    h+='</div>'
  }
  var tot=ta.in+ta.out+ta.ca;
  h+='<div class="sum"><span class="lb">合计（所有模型）</span><span>';
  h+='<span class="in">输入 '+F(ta.in)+'</span> &nbsp; ';
  h+='<span class="out">输出 '+F(ta.out)+'</span> &nbsp; ';
  h+='<span class="ca">缓存 '+F(ta.ca)+'</span> &nbsp; ';
  h+='<b>总计 '+F(tot)+'</b></span></div>';
  h+='<div class="quit-wrap"><button class="quit-btn" onclick="quit()"><span>⏻</span><span>退出</span></button></div>';
  c.innerHTML=h
}

function $(id){return document.getElementById(id)}
function swTab(t){tab=t;$("tb-pi").classList.toggle("on",t==="pi-agent");$("tb-oc").classList.toggle("on",t==="opencode");R();reportH()}
function swRng(r){rng=r;$("bt-td").classList.toggle("on",r==="today");$("bt-wk").classList.toggle("on",r==="week");$("bt-mo").classList.toggle("on",r==="month");R();reportH()}
function refresh(){webkit.messageHandlers.refresh.postMessage("go")}
function quit(){webkit.messageHandlers.quit.postMessage("go")}
function load(j){D=JSON.parse(j);R();reportH()}
function reportH(){webkit.messageHandlers.height.postMessage(document.body.scrollHeight)}
R();reportH()
</script></body></html>"""


# ── App delegate ────────────────────────────────────────────────────────────


class Delegate(NSObject):
    """NSApplication delegate that owns the status item, popover, and timer."""

    def init(self):
        self = super().init()
        if self is None:
            return None

        # Data
        self.all_data: dict = {}

        # Status item
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        btn = self.status_item.button()
        btn.setTitle_("📊")
        btn.setToolTip_("Token Dashboard")
        btn.setTarget_(self)
        btn.setAction_("togglePopover:")

        # Popover
        self.popover = NSPopover.alloc().init()
        self.popover.setBehavior_(NSPopoverBehaviorTransient)
        self.popover.setContentSize_((310, 160))

        # WebView
        self.webview = None
        self._setup_webview()

        # Timer
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            30.0, self, "timerFired:", None, True
        )

        # Initial load
        self.refresh_data()

        return self

    def _setup_webview(self):
        config = WKWebViewConfiguration.alloc().init()
        controller = config.userContentController()
        controller.addScriptMessageHandler_name_(self, "refresh")
        controller.addScriptMessageHandler_name_(self, "height")
        controller.addScriptMessageHandler_name_(self, "quit")

        size = self.popover.contentSize()
        rect = NSMakeRect(0, 0, size.width, size.height)
        self.webview = WKWebView.alloc().initWithFrame_configuration_(rect, config)

        vc = NSViewController.alloc().init()
        vc.setView_(self.webview)
        self.popover.setContentViewController_(vc)

        # Load HTML template
        self.webview.loadHTMLString_baseURL_(HTML, None)

    def refresh_data(self):
        """Read all sources, aggregate, and update webview."""
        try:
            now = datetime.now(timezone.utc)
            # Serialize now for output
            now_iso = now.isoformat()
        except Exception:
            return

        all_records = read_pi_agent_sessions() + read_opencode_sessions()
        grouped = aggregate(all_records, now)

        # Convert to JSON-serializable shape
        out: dict = {}
        for source, buckets in grouped.items():
            src_data: dict = {}
            for bname, binfo in buckets.items():
                models_out: dict = {}
                for model, stats in binfo["models"].items():
                    models_out[model] = {
                        "input": stats.input,
                        "output": stats.output,
                        "cache_read": stats.cache_read,
                    }
                src_data[bname] = {"models": models_out}
            out[source] = src_data

        self.all_data = out
        self._push_to_webview(out)

    def _push_to_webview(self, data: dict):
        """Inject updated data into the webview via JS."""
        if self.webview is None:
            return
        json_str = json.dumps(data, ensure_ascii=False)
        js = f"load({json.dumps(json_str)})"
        self.webview.evaluateJavaScript_completionHandler_(js, None)

    # ── selectors ───────────────────────────────────────────────────────

    def togglePopover_(self, sender):
        if self.popover.isShown():
            self.popover.close()
        else:
            btn = self.status_item.button()
            self.popover.showRelativeToRect_ofView_preferredEdge_(
                btn.bounds(), btn, 1  # 1 = MinYEdge (below)
            )
            self.refresh_data()

    def timerFired_(self, timer):
        self.refresh_data()

    # ── WKScriptMessageHandler ──────────────────────────────────────────

    def userContentController_didReceiveScriptMessage_(self, controller, message):
        name = message.name()
        if name == "refresh":
            self.refresh_data()
        elif name == "quit":
            NSApplication.sharedApplication().terminate_(None)
        elif name == "height":
            try:
                h = int(message.body()) + 8  # + padding
                if h > 80:
                    self.popover.setContentSize_((310, min(h, 600)))
            except (ValueError, TypeError):
                pass


# ── Entry point ─────────────────────────────────────────────────────────────


def main():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    delegate = Delegate.alloc().init()  # noqa: F841 – held alive by app

    app.activateIgnoringOtherApps_(True)
    app.run()


if __name__ == "__main__":
    main()
