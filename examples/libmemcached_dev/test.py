import ctypes
import pymemcached as mmc

print 'memcached version: ', mmc.memcached_lib_version()

memc = mmc.memcached_create(None)
servers = mmc.memcached_servers_parse( "localhost:11211" )
mmc.memcached_server_push(memc, servers);
mmc.memcached_server_list_free(servers);

key = "1"
value = "Python is better!"

result = mmc.memcached_add( memc, key, len(key), value, len(value), 0, 0);
print "key/value (%s/%s ) was stored?: " % ( key, value ) + mmc.memcached_strerror(memc, result);

result = mmc.memcached_delete( memc, key, len(key), 0);
print "key/value (%s/%s ) was deleted?: " % ( key, value ) + mmc.memcached_strerror(memc, result);
