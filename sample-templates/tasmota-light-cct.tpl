Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto) {
    Channels:
        Type switch: power	    [ stateTopic="stat/{{thingid}}/RESULT", transformationPattern="REGEX:(.*POWER.*)∩JSONPATH:$.POWER", commandTopic="cmnd/{{thingid}}/POWER" ]
        Type dimmer: dimmer     [ stateTopic="stat/{{thingid}}/RESULT", transformationPattern="REGEX:(.*Dimmer.*)∩JSONPATH:$.Dimmer", commandTopic="cmnd/{{thingid}}/Dimmer" ]
        Type dimmer: ct         [ stateTopic="stat/{{thingid}}/RESULT", transformationPattern="REGEX:(.*CT.*)∩JSONPATH:$.CT", commandTopic="cmnd/{{thingid}}/CT", min=153, max=500, step=1 ]
        Type switch: reachable  [ stateTopic="tele/{{thingid}}/LWT", on="Online", off="Offline" ]
        Type number: rssi	    [ stateTopic="tele/{{thingid}}/STATE", transformationPattern="JSONPATH:$.Wifi.RSSI" ]
        Type string: state      [ stateTopic="tele/{{thingid}}/dummy", commandTopic="cmnd/{{thingid}}/STATE" ]
}

Switch {{name}}_Power  "{{label}} Power" <light> {{groups}} { channel="mqtt:topic:mosquitto:{{thingid}}:power", autoupdate="false" }
Dimmer {{name}}_Dimmer "{{label}}" { channel="mqtt:topic:mosquitto:{{thingid}}:dimmer"{% for m in metadata: %}, {{m}}{%endfor%} }
Dimmer {{name}}_CT     "{{label}} CT"            { channel="mqtt:topic:mosquitto:{{thingid}}:ct" }
Number {{name}}_RSSI   "{{label}} RSSI [%d%%]" <network> (gSignalStrength) { channel="mqtt:topic:mosquitto:{{thingid}}:rssi" }
String {{name}}_State   (gTasmotaState)          { channel="mqtt:topic:mosquitto:{{thingid}}:state" }
