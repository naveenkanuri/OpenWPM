import { getInstrumentJS, JSInstrumentRequest } from "../lib/js-instruments";
import { pageScript } from "./javascript-instrument-page-scope";
import { openWpmContentScriptConfig } from "../types/javascript-instrument";

function getPageScriptAsString(
  jsInstrumentationSettings: JSInstrumentRequest[],
): string {
  // The JS Instrument Requests are setup and validated python side
  // including setting defaults for logSettings. See JSInstrumentation.py
  const pageScriptString = `
// Start of js-instruments.
${getInstrumentJS}
// End of js-instruments.

// Start of custom instrumentRequests.
const jsInstrumentationSettings = ${JSON.stringify(jsInstrumentationSettings)};
// End of custom instrumentRequests.

// Start of anonymous function from javascript-instrument-page-scope.ts
(${pageScript}(getInstrumentJS, jsInstrumentationSettings));
// End.
  `;
  return pageScriptString;
}

function insertScript(
  pageScriptString: string,
  eventId: string,
  testing: boolean = false,
) {
  const parent = document.documentElement;
  const script = document.createElement("script");
  script.text = pageScriptString;
  script.async = false;
  script.setAttribute("data-event-id", eventId);
  script.setAttribute("data-testing", `${testing}`);
  parent.insertBefore(script, parent.firstChild);
  parent.removeChild(script);
  // document.addEventListener("mousemove", (event : MouseEvent) => {
  //     // console.log("eventId = " +eventId + ", Mouse position: " + event.clientX + ", " + event.clientY);
  //     emitMsg('logCall', "hello + eventId = " +eventId + ", Mouse position: " + event.clientX + ", " + event.clientY);
  //   });
  console.log('hello from content-scope.ts')
}

function emitMsg(type, msg) {
  msg.timeStamp = new Date().toISOString();
  browser.runtime.sendMessage({
    namespace: "javascript-instrumentation",
    type,
    data: msg,
  });
}

const eventId = Math.random().toString();

// listen for messages from the script we are about to insert
document.addEventListener(eventId, (e: CustomEvent) => {
  // pass these on to the background page
  const msgs = e.detail;
  if (Array.isArray(msgs)) {
    msgs.forEach((msg) => {
      // console.log('msg.type = ' +msg.type + ' msg.content = '+msg.content);
      // console.log(JSON.stringify(msg.content));
      emitMsg(msg.type, msg.content);
    });
  } else {
    // console.log('msg.type = ' +msgs.type + ' msg.content = '+msgs.content);
    // console.log(JSON.stringify(msgs.content));
    emitMsg(msgs.type, msgs.content);
  }
});

// document.addEventListener("mousemove", (event : MouseEvent) => {
//       console.log("Mouse position: " + event.clientX + ", " + event.clientY);
//     });


export const injectJavascriptInstrumentPageScript = (
  contentScriptConfig: openWpmContentScriptConfig,
) => {
  insertScript(
    getPageScriptAsString(contentScriptConfig.jsInstrumentationSettings),
    eventId,
    contentScriptConfig.testing,
  );
};
