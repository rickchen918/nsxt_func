# import the function call script tlr.py
# Create T0 router and T0 port for T1 connects
# Create T1 router and T1 port connects to T0
# Create Logical switch and Logical switch port
# Create T1 router port connects to logical switchs port
# This script has dependence with tlr.py 

import tlr
modeA="ACTIVE_ACTIVE"
modeS="ACTIVE_STANDBY"
esgid=tlr.esg_id()
zoneid=tlr.tz_id().get('OVERLAY')
# below defines the number of network creation aligns with T0/T1 creation. 
# Comply with exisitng function specification, just create single T0 router on edge cluster
# the subnet range creation will be 172.16.(t1_count+lsw_count).1
t0_count=1
t1_count=20
lsw_count=3

# the loop to generate logical router configuration
i=0
while i<t0_count:
    t0_rtid=tlr.create_lr0("rkc_t0_"+str(i),"TIER0",modeA,esgid)
    print "creating logical router T0 ",t0_rtid
    j=1
    while j<t1_count:
        t0_lport=tlr.create_lr0_port(t0_rtid)
	print "creating T0 logica port for T1 ",t0_lport
        t1_rtid=tlr.create_lr1("rkc_t1_"+str(i)+str(j),esgid,"TIER1",modeS)
        print "creating logical router T1 ",t0_rtid
        t1_lport=tlr.create_lr1_port(t1_rtid,t0_lport)
        print "creating T1 logical port for T0 ",t1_lport
        k=0
	while k<lsw_count:
            lsw=tlr.create_lsw("lsw"+str(i)+str(j)+str(k),zoneid)
	    print "creating logical switch ",lsw
            lswport=tlr.create_lswport(lsw)
	    print "creating logical switch port ",lswport
            lrdownlink=tlr.create_lrdownlink(t1_rtid,lswport,"172."+str(j)+"."+str(k)+".1")
	    print "create T1 logical downlink", lrdownlink
            k+=1
        j+=1
    print "the "+str(i) +"topo has been created"
    print "#"*130
    i+=1

## attach vlan interface to T0 
zoneid=tlr.tz_id().get('VLAN')
vlan_lsw=tlr.create_vlanlsw('vlan_uplink',zoneid,'0')
lswport0=tlr.create_lswport(vlan_lsw)
lswport1=tlr.create_lswport(vlan_lsw)
t0_id=tlr.get_t0_id()
t0_uplink0=tlr.create_lruplink(t0_id,lswport0,"192.168.100.20","0")
t0_uplink1=tlr.create_lruplink(t0_id,lswport1,"192.168.100.23","1")


# enable bgp process on T0
# the 65001 is local bgp as number and configurable 
bgproc=tlr.en_router_bgp_proc(t0_id,"65001")

# configure bgp peer to CSR router
# the 65000 is remote bgp as number and configurable
peer=tlr.en_router_bgp_peer(t0_id,"192.168.100.21","65000")

# enable bfd on T0
tlr.en_bfd(t0_id,"true","300","300","3")

# enable bfd on T0 peer
tlr.en_router_bgp_peer_bfd(t0_id)

# enable redistribution on T0
redist=tlr.en_router_redist(t0_id)

# cerate redistribution rule on T0
tlr.en_router_redist_rule(t0_id,"NSX_STATIC","Test")

# enable T1 router having connected advertisement 
t1_id=tlr.get_t1_id()
for run in t1_id:
    tlr.en_router_adv(run)

# enable source nat all on T1 router and T0 only propagate nat route
#tlr.en_router_redist_rule(t0_id,"TIER1_NAT","Test1")
length=len(t1_id)
for run2 in t1_id:
    source_net="172.0.0.0/8"
    i=length
    translated_net="192.168.120.%s/32"%i
#    tlr.snat_all(run2,source_net,translated_net)
    length-=1
