	# The script is function call for nsxt logical routing topology building. 
# You can create orchestrator script to call this function script. 
# It could make work to  look simplification ffrom different function aspect.   
# The author is Rick Chen, Sr.Soltuion Architect of VMware

import requests,json,base64,paramiko,pdb
requests.packages.urllib3.disable_warnings()

################# define api call envionment variable  #################
mgr="192.168.64.186"
mgruser="admin"
mgrpasswd="Nicira123$"
cred=base64.b64encode('%s:%s'%(mgruser,mgrpasswd))
header={"Authorization":"Basic %s"%cred,"Content-type":"application/json"}

 
# edge cluster id retreive 
def esg_id():
    ep="/api/v1/edge-clusters"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    data=json.loads(conn.text)
    x=data.get('results')
    for y in x:
        z=y.get('id')
        return z

# transport zone id retreive
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

# create T0 logical router
def create_lr0(name,type0,mode0,esgid):
    ep="/api/v1/logical-routers"
    url="https://"+str(mgr)+str(ep)
    body="""{
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
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create T0 logical router port for T1 connectivity 
def create_lr0_port(lr00id):
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
    body="""{
            "logical_router_id":"%s",
            "resource_type":"LogicalRouterLinkPortOnTIER0"
              }"""%(lr00id)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create T0 uplink port to vlan, here is supposed to have only one edge cluster
# the cluster memner index is the edge number index of edge cluster
def create_lruplink(lr00id,lswport,subnet,member):
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
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
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create t1 logical router
def create_lr1(name,esgid,type1,mode1):
    ep="/api/v1/logical-routers"
    url="https://"+str(mgr)+str(ep)
    body="""{
        "resource_type": "LogicalRouter",
        "description": "",
        "display_name": "%s",
	"edge_cluster_id": "%s",
        "advanced_config": {
        "internal_transit_network": "169.254.0.0/28"
        },
        "router_type": "%s",
        "high_availability_mode": "%s"
        }"""%(name,esgid,type1,mode1)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create t1 logical router port to connect T0 
def create_lr1_port(lr10id,lr00portid):
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
    body="""{
        "resource_type":"LogicalRouterLinkPortOnTIER1",
        "logical_router_id":"%s",
        "linked_logical_router_port_id": {
        "target_display_name": "LinkedPort_T1_Uplink",
        "is_valid": true,
        "target_type": "LogicalRouterLinkPortOnTIER0",
        "target_id": "%s"
         }
        }"""%(lr10id,lr00portid)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create t1 donwlink port to connect logical switch 
def create_lrdownlink(lr10id,lswport,subnet):
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
    body="""{
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
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    print conn.text
    return result

################# create logical switch configuration #################

# create logical switch for overlay
def create_lsw(lswname,zoneid):
    ep="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(ep)
    body="""{
 	    "transport_zone_id":"%s",
  	    "replication_mode": "MTEP",
             "admin_state":"UP",
             "display_name":"%s"
	    }"""%(zoneid,lswname)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create logical switch for vlan
def create_vlanlsw(lswname,zoneid,vlan):
    ep="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(ep)
    body="""{
            "transport_zone_id":"%s",
             "admin_state":"UP",
             "display_name":"%s",
	     "vlan":"%s"
            }"""%(zoneid,lswname,vlan)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

# create logical switch port for t0/t1 router connecting
def create_lswport(lswid):
    ep="/api/v1/logical-ports"
    url="https://"+str(mgr)+str(ep)
    body="""{
  	"logical_switch_id":"%s",
  	"admin_state":"UP"
		}"""%(lswid)
    conn=requests.post(url,verify=False,headers=header,data=body)
    result=json.loads(conn.text).get('id')
    return result

################# delete tlr configuration #################

# delete logical router
def delete_lr():
    ep="/api/v1/logical-routers"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
	id=x.get('id')
	matrix.append(id)

    for y in matrix:
	id=y
	url_1=url+"/"+id+str("?force=true")
	conn=requests.delete(url_1,verify=False,headers=header)

# delete logical router port
def delete_lrport():
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url_1=url+"/"+id+str("?force=true")
        conn=requests.delete(url_1,verify=False,headers=header)

# delete logical switch 
def delete_lsw():
    ep="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url_1=url+"/"+id
        conn=requests.delete(url_1,verify=False,headers=header)

# delete logical swtch port
def delete_lswport():
    ep="/api/v1/logical-ports"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for x in result:
        id=x.get('id')
        matrix.append(id)

    for y in matrix:
        id=y
        url_1=url+"/"+id
        conn=requests.delete(url_1,verify=False,headers=header)

################# count tlr configuration #################

# Due to page size is limited on 1000, so if the number of property is over 1K
# The delete call needs to have another around to clear it. so This function is
# mainly to  retrive the resount_count and be calculated under orchestrrators script 

# count logical router port
def lrport_count():
    ep="/api/v1/logical-router-ports"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

# count logical router
def lr_count():
    ep="/api/v1/logical-routers"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

# count logical switch port
def lswport_count():
    ep="/api/v1/logical-ports"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

# count logical switch 
def lsw_count():
    ep="/api/v1/logical-switches"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    count=json.loads(conn.text).get('result_count')
    return count

    conn_1=requests.get(url,verify=False,headers=header)
    result=json.loads(conn_1.text).get('results')

################# get tlr configuration #################

# retrive t0 router id 
def get_t0_id():
    ep="/api/v1/logical-routers?router_type=TIER0"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    for t0 in result:
	id=t0.get('id')
    return id

# retrive t1 router id
def get_t1_id():
    ep="/api/v1/logical-routers?router_type=TIER1"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for t0 in result:
        id=t0.get('id')
	matrix.append(id)
    return matrix

################# configure routing configuration #################

# enable and configure t1 redistribution
# this function call is only working for T1, T0 is not supported
def en_router_adv(t1_uuid):
    ep="/api/v1/logical-routers/%s/routing/advertisement"%(t1_uuid)
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    version=json.loads(conn.text).get('_revision')
    body="""{
        "advertise_nsx_connected_routes": true,
        "advertise_static_routes": false,
        "advertise_nat_routes": true,
        "enabled": true,
	"_revision": "%s"
        }"""%version
    conn1=requests.put(url,verify=False,headers=header,data=body)
    print conn1.text

# this function call is to enable the T0 redistribution 
def en_router_redist(t0_uuid):
    ep="/api/v1/logical-routers/%s/routing/redistribution"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    version=json.loads(conn.text).get('_revision')
    body="""{
        "bgp_enabled":"true",
        "_revision": "%s"
        }"""%version
    conn1=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

# The function call is to configure "redistribution source", the source option is
# STATIC,NSX_CONNECTED,NSX_STATIC,TIER0_NAT,TIER1_NAT 
def en_router_redist_rule(t0_uuid,source,name):
    ep="/api/v1/logical-routers/%s/routing/redistribution/rules"%(t0_uuid)
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    version=json.loads(conn.text).get('_revision') 
    body="""{
	 "_revision": %s,
  	"rules": [
    	{
      	"display_name":"%s",
      	"destination":"BGP",
      	"sources":["%s"]
    	}
  	]
        }"""%(version,name,source)
    conn1=requests.put(url,verify=False,headers=header,data=body)
    print conn.text

# enable t0 bgp process
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

# configure bgp peering on t0
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

# configure snat 
def snat_all(t1_uuid,source_net,translated_net):
    ep="/api/v1/logical-routers/%s/nat/rules"%(t1_uuid)
    url="https://"+str(mgr)+str(ep)
    body="""{
	"action": "SNAT",
    	"match_source_network": "%s",
    	"translated_network": "%s",
    	"enabled": true
	}"""%(source_net,translated_net)
    conn=requests.post(url,verify=False,headers=header,data=body)
    print conn.text


################# list tlr configuration #################

def list_t1_router_lif():
    ep="/api/v1/logical-router-ports?resource_type=LogicalRouterDownLinkPort"
    url="https://"+str(mgr)+str(ep)
    conn=requests.get(url,verify=False,headers=header)
    result=json.loads(conn.text).get('results')
    matrix=[]
    for net in result:
	subnet=net.get('subnets')
        matrix.append(subnet)
    return matrix
    matrix_1=[]
    for ip in matrix:
	position=ip[0]
	ip_addr=position.get('ip_addresses')
	matrix_1.append(ip_addr)
	print matrix_1
    matrix_1.sort()
    return matrix_1

