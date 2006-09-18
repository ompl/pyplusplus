import cspc_ext

def test_instance( inst ):
    print "call val_get_value( inst ) => %d" % cspc_ext.val_get_value(inst)
    try:
        #this will give us Segmentation fault on Linux
        #But if you comment previuos statement than all will be fine.
        print "call const_ref_get_value( inst ) => %d" % cspc_ext.const_ref_get_value(inst)
    except Exception, error:
        print "\nUnable to call const_ref_get_value( inst ): ", str(error)

print 'testing derived_t instance'
inst = cspc_ext.derived_t()
test_instance( inst )
print 'testing derived_t instance - done'
