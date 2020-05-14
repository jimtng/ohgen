Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto) {
    Channels:
        Type contact : occupancy    [ stateTopic="zigbee/{{thingid}}/occupancy", on="true", off="false"  ]
        Type number  : illuminance  [ stateTopic="zigbee/{{thingid}}/illuminance" ]
        Type number  : linkquality  [ stateTopic="zigbee/{{thingid}}/linkquality" ]
        Type switch  : reachable    [ stateTopic="zigbee/{{thingid}}/availability", on="online", off="offline" ]
        Type number  : battery      [ stateTopic="zigbee/{{thingid}}/battery" ]
}

Contact {{name_parts[0]}}_Motion       "{{room}} Motion" <motion> {{groups}}  { channel="mqtt:topic:mosquitto:{{thingid}}:occupancy" }
Number  {{name}}_Illuminance  "{{room}} Illuminance"             (gIlluminance) { channel="mqtt:topic:mosquitto:{{thingid}}:illuminance" }
Number  {{name}}_Link         "{{label}} Link"      <network> (gSignalStrength) { channel="mqtt:topic:mosquitto:{{thingid}}:linkquality" }
Number  {{name}}_Battery      "{{label}} Battery [%d%%]" <battery> (gBatteries) { channel="mqtt:topic:mosquitto:{{thingid}}:battery", expire="1h" }
