import requests,json,base64,paramiko,pdb
#requests.packages.urllib3.disable_warnings()

mgr="192.168.64.186"
mgruser="admin"
mgrpasswd="Nicira123$"
cred=base64.b64encode('%s:%s'%(mgruser,mgrpasswd))
header={"Authorization":"Basic %s"%cred,"Content-type":"application/json"}

#edge cluster id acquire
def esg_id():
    ep="/api/v1/edge-clusters"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    data=json.loads(conn.text)
    x=data.get('results')
    for y in x:
        z=y.get('id')
        return z

def tz_id():
    eptz="/api/v1/transport-zones"
    url="https://"+str(mgr)+str(eptz)
    conn=requests.get(url,verify=False,headers=header)
    data=json.loads(conn.text)
    result=data.get('results')
    matrix={}
    for x in result:
	type=x.get('transport_type')
	tzid=x.get('id')
	pair={type:tzid}
	matrix.update(pair)
    return matrix

################# create logical router  configuration #################

def create_lr0(name,type0,mode0,esgid):
    lr_ep="/api/v1/logical-routers"
    lr_url="https://"+str(mgr)+str(lr_ep)
    body00="""{
            "resource_type": "LogicalRouter",
            "description": "",
            "display_name": "%s",
            "edge_cluster_id": "%s",
            "advanced_config": {
            "external_transit_networks": [
            "100.64.0.0/16"
             ],
            "internal_transit_network": "169.254.0.0/28"
             },
             "router_type": "%s",
             "high_availability_mode": "%s"
             }"""%(name,esgid,type0,mode0)
    conn00=requests.post(lr_url,verify=False,headers=header,data=body00)
    data00=json.loads(conn00.text)
    lr00id=data00.get('id')
    return lr00id

def create_lr0_port(lr00id):
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    body01="""{
            "logical_router_id":"%s",
            "resource_type":"LogicalRouterLinkPortOnTIER0"
              }"""%(lr00id)
    conn01=requests.post(lr_port_url,verify=False,headers=header,data=body01)
    data01=json.loads(conn01.text)
    lr00portid=data01.get('id')
    return lr00portid

def create_lruplink(lr00id,lswport,subnet,member):
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    body="""{
        "resource_type": "LogicalRouterUpLinkPort",
        "logical_router_id": "%s",
        "linked_logical_switch_port_id":{
                "target_type": "LogicalPort",
                "target_id": "%s"
                },
	"edge_cluster_member_index":[
		%s
	],
         "subnets": [
                {
                 "ip_addresses": [
                        "%s"
                ],
                 "prefix_length": 24
                }
                ]
        }"""%(lr00id,lswport,member,subnet)
    conn=requests.post(lr_port_url,verify=False,headers=header,data=body)
    print conn.text
    data=json.loads(conn.text)
    lr10portid=data.get('id')
    return lr10portid

def create_lr1(name,type1,mode1):
    lr_ep="/api/v1/logical-routers"
    lr_url="https://"+str(mgr)+str(lr_ep)
    body10="""{
        "resource_type": "LogicalRouter",
        "description": "",
        "display_name": "%s",
        "advanced_config": {
        "internal_transit_network": "169.254.0.0/28"
        },
        "router_type": "%s",
        "high_availability_mode": "%s"
        }"""%(name,type1,mode1)
    conn10=requests.post(lr_url,verify=False,headers=header,data=body10)
    data10=json.loads(conn10.text)
    lr10id=data10.get('id')
    return lr10id

def create_lr1_port(lr10id,lr00portid):
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    body11="""{
        "resource_type":"LogicalRouterLinkPortOnTIER1",
        "logical_router_id":"%s",
        "linked_logical_router_port_id": {
        "target_display_name": "LinkedPort_T1_Uplink",
        "is_valid": true,
        "target_type": "LogicalRouterLinkPortOnTIER0",
        "target_id": "%s"
         }
        }"""%(lr10id,lr00portid)
    conn11=requests.post(lr_port_url,verify=False,headers=header,data=body11)
    data11=json.loads(conn11.text)
    lr10portid=data11.get('id')
    return lr10portid

def create_lrdownlink(lr10id,lswport,subnet):
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    body12="""{
        "resource_type": "LogicalRouterDownLinkPort",
        "logical_router_id": "%s",
        "linked_logical_switch_port_id":{
                "target_type": "LogicalPort",
                "target_id": "%s"
                },
         "subnets": [
                {
                 "ip_addresses": [
                        "%s"
                ],
                 "prefix_length": 24
                }
                ]
        }"""%(lr10id,lswport,subnet)
    conn12=requests.post(lr_port_url,verify=False,headers=header,data=body12)
    data12=json.loads(conn12.text)
    lr10portid=data12.get('id')
    return lr10portid

################# create logical switch configuration #################

def create_lsw(lswname,zoneid):
    eplsw="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(eplsw)
    bodysw="""{
 	    "transport_zone_id":"%s",
  	    "replication_mode": "MTEP",
             "admin_state":"UP",
             "display_name":"%s"
	    }"""%(zoneid,lswname)
    conn=requests.post(url,verify=False,headers=header,data=bodysw)
    lswid=json.loads(conn.text).get('id')
    return lswid

def create_vlanlsw(lswname,zoneid,vlan):
    eplsw="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(eplsw)
    bodysw="""{
            "transport_zone_id":"%s",
             "admin_state":"UP",
             "display_name":"%s",
	     "vlan":"%s"
            }"""%(zoneid,lswname,vlan)
    conn=requests.post(url,verify=False,headers=header,data=bodysw)
    lswid=json.loads(conn.text).get('id')
    return lswid

def create_lswport(lswid):
    eplport="/api/v1/logical-ports"
    url="https://"+str(mgr)+str(eplport)
    bodylport="""{
  	"logical_switch_id":"%s",
  	"admin_state":"UP"
		}"""%(lswid)
    conn=requests.post(url,verify=False,headers=header,data=bodylport)
    lportid=json.loads(conn.text).get('id')
    return lportid

################# delete tlr configuration #################

def delete_lr():
    lr_ep="/api/v1/logical-routers"
    lr_url="https://"+str(mgr)+str(lr_ep)
    conn=requests.get(lr_url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
	id=x.get('id')
	matrix.append(id)

    for y in matrix:
	id=y
	url=lr_url+"/"+id+str("?force=true")
	conn=requests.delete(url,verify=False,headers=header)

def delete_lrport():
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    conn=requests.get(lr_port_url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url=lr_port_url+"/"+id+str("?force=true")
        conn=requests.delete(url,verify=False,headers=header)

def delete_lsw():
    lsw_ep="/api/v1/logical-switches"
    lsw_url="https://"+str(mgr)+str(lsw_ep)
    conn=requests.get(lsw_url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url=lsw_url+"/"+id
        conn=requests.delete(url,verify=False,headers=header)
        conn1=requests.get(url,verify=False,headers=header)

def delete_lswport():
    lsw_port_ep="/api/v1/logical-ports"
    lsw_port_url="https://"+str(mgr)+str(lsw_port_ep)
    conn=requests.get(lsw_port_url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url=lsw_port_url+"/"+id
        conn=requests.delete(url,verify=False,headers=header)
        conn1=requests.get(url,verify=False,headers=header)

################# count tlr configuration #################

def lrport_count():
    lr_port_ep="/api/v1/logical-router-ports"
    lr_port_url="https://"+str(mgr)+str(lr_port_ep)
    conn=requests.get(lr_port_url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

def lr_count():
    lr_ep="/api/v1/logical-routers"
    lr_url="https://"+str(mgr)+str(lr_ep)
    conn=requests.get(lr_url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count


def lswport_count():
    lsw_port_ep="/api/v1/logical-ports"
    lsw_port_url="https://"+str(mgr)+str(lsw_port_ep)
    conn=requests.get(lsw_port_url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

def lsw_count():
    lsw_port_ep="/api/v1/logical-switches"
    lsw_port_url="https://"+str(mgr)+str(lsw_port_ep)
    conn=requests.get(lsw_port_url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')

################# get tlr configuration #################

def get_t0_id():
    t0_ep="/api/v1/logical-routers?router_type=TIER0"
    url="https://"+str(mgr)+str(t0_ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    for t0 in result:
	id=t0.get('id')
    return id

def get_t1_id():
    t1_ep="/api/v1/logical-routers?router_type=TIER1"
    url="https://"+str(mgr)+str(t1_ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for t0 in result:
        id=t0.get('id')
	matrix.append(id)
    return matrix

################# allocate tlr configuration #################

# this function call is only working for T1, T0 is not supported
def en_router_adv(t1_uuid):
    ep="/api/v1/logical-routers/%s/routing/advertisement"%(t1_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
        "advertise_nsx_connected_routes": true,
        "advertise_static_routes": false,
        "advertise_nat_routes": true,
        "enabled": true,
	"_revision": "0"
        }"""
    conn=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

# this function call is to enable the T0 redistribution (not test yet)
def en_router_redist(t0_uuid):
    ep="/api/v1/logical-routers/%s/routing/redistribution"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
        "bgp_enabled":"true"
        }"""
    conn=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

# The function call is to configure "redistribution source", the source option is
# STATIC,NSX_CONNECTED,NSX_STATIC,TIER0_NAT,TIER1_NAT (no test yet)
def en_router_redist_rule(t0_uuid,source,name):
   ep="/api/v1/logical-routers/%s/routing/redistribution/rules"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
        "rules": [
        {
            "sources": [
                "%s"
            ],
            "destination": "BGP",
            "display_name": "%s"
        }
        ]
        }"""%(t0_uuid,source,name)
    conn=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

def en_router_bgp_proc(t0_uuid,local_as):
    ep="/api/v1/logical-routers/%s/routing/bgp"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
  	"resource_type": "BgpConfig",
  	"as_num": "%s",
  	"graceful_restart": true,
  	"enabled": true,
  	"ecmp": false,
  	"_revision": "0"
	}"""%(local_as)
    conn=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

def en_router_bgp_peer(t0_uuid,neig_addr,remo_as):
    ep="/api/v1/logical-routers/%s/routing/bgp/neighbors"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
	"resource_type":"BgpNeighbor",
 	"display_name": "",
  	"neighbor_address": "%s",
  	"remote_as_num": "%s",
  	"address_families": [
    	{
      	"type" : "IPV4_UNICAST",
      	"enabled" : true
    	 }
  	]
	}"""%(neig_addr,remo_as)
    conn=requests.post(url,verify=False,headers=header,data=body)
    print conn.text
