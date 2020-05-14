Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto) {
    Channels:
        Type switch : power	           [ stateTopic="stat/{{thingid}}/RESULT", transformationPattern="JSONPATH:$.POWER", commandTopic="cmnd/{{thingid}}/POWER" ]
        Type switch : reachable	  [ stateTopic="tele/{{thingid}}/LWT", on="Online", off="Offline" ]
        Type number : rssi	     [ stateTopic="tele/{{thingid}}/STATE", transformationPattern="JSONPATH:$.Wifi.RSSI" ]
        Type string : state           [ stateTopic="tele/{{thingid}}/dummy", commandTopic="cmnd/{{thingid}}/STATE" ]
}

Switch {{name}}_Power  "{{label}} Power" {% if icon %}{{icon}}{%else%}<switch>{%endif%} {{groups}}{%for tag in tags%}{%if loop.first%} [{%else%}, {%endif%}"{{tag}}"{%if loop.last%}] {%endif%}{%endfor%} { channel="mqtt:topic:mosquitto:{{thingid}}:power", autoupdate="false"{% for m in metadata: %}, {{m}}{%endfor%} }
Number {{name}}_RSSI   "{{label}} RSSI [%d%%]" <network> (gSignalStrength)  { channel="mqtt:topic:mosquitto:{{thingid}}:rssi" }
String {{name}}_State	(gTasmotaState)                           { channel="mqtt:topic:mosquitto:{{thingid}}:state" }
