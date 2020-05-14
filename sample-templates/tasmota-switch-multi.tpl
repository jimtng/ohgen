Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto) {
    Channels:
{%- for item in switches:%}
        Type switch : power{{loop.index}}    [ stateTopic="stat/{{thingid}}/RESULT", transformationPattern="JSONPATH:$.POWER{{loop.index}}", commandTopic="cmnd/{{thingid}}/POWER{{loop.index}}" ]
{%- endfor%}
        Type switch : reachable [ stateTopic="tele/{{thingid}}/LWT", on="Online", off="Offline" ]
        Type number : rssi      [ stateTopic="tele/{{thingid}}/STATE", transformationPattern="JSONPATH:$.Wifi.RSSI" ]
        Type string : state     [ stateTopic="tele/{{thingid}}/dummy", commandTopic="cmnd/{{thingid}}/STATE" ]
}

{%- for item in switches:%}
Switch {{item['name']}}_Power "{{item['label']}}" <switch> {{item['groups']}} { channel="mqtt:topic:mosquitto:{{thingid}}:power{{loop.index}}", autoupdate="false"{% for m in metadata: %}, {{m}}{%endfor%} }
{%- endfor%}
Number {{name}}_RSSI   "{{label}} RSSI [%d%%]"  <network> (gSignalStrength)  { channel="mqtt:topic:mosquitto:{{thingid}}:rssi" }
String {{name}}_State	(gTasmotaState)                            { channel="mqtt:topic:mosquitto:{{thingid}}:state" }
