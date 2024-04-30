local p_rdt_protocol_g_09 = Proto("rdt_protocol_g_09", "RDT G9")


local message_type = ProtoField.uint8("rdt_protocol_g_09.message_type", "Type")
local seq_num = ProtoField.uint32("rdt_protocol_g_09.seq_num", "Sequence Number")
local data = ProtoField.bytes("rdt_protocol_g_09.data", "Data")


p_rdt_protocol_g_09.fields = {
    message_type,
    seq_num,
    data
}

function p_rdt_protocol_g_09.dissector(buf, pinfo, tree)
    local subtree = tree:add(p_rdt_protocol_g_09, buf())

    subtree:add(message_type, buf(0, 1))
    subtree:add(seq_num, buf(1, 4))
    subtree:add(data, buf(5))


    pinfo.cols.protocol:set("RDT G9")
end


local udp_port = DissectorTable.get("udp.port")
udp_port:add(6653, p_rdt_protocol_g_09)
