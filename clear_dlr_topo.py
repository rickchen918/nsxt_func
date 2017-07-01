# viloate way to remove all logical switch and router configuration 
# Delete logical router ports
# Delete logical routers 
# Delete logical switch ports
# Delete logical switches 

import tlr,json,requests

#delete logical router ports 
lrport_count=tlr.lrport_count()
call=(lrport_count/1000)+1
while call >=0:
    tlr.delete_lrport()
    call-=1
print "The logical router ports have been deleted"
print "#"*130

#delete logical routers
lr_count=tlr.lr_count()
call=(lr_count/1000)+1
while call >=0:
    tlr.delete_lr()
    call-=1
print "The logical router have been deleted"
print "#"*130

# delete logical switch ports
lswport_count=tlr.lswport_count()
call=(lswport_count/1000)+1
while call >=0:
    tlr.delete_lswport()
    call-=1
print "The logical switch ports have been deleted"
print "#"*130

# delete logical switches
lsw_count=tlr.lsw_count()
call=(lsw_count/1000)+1
while call >=0:
    tlr.delete_lsw()
    call-=1
print "The logical switch ports have been deleted"
print "#"*130

