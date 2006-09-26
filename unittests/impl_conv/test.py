import operators_ext

print 'envoke operator+ using old Boost.Python interface'
old = operators_ext.vector_old()
tmp = old + operators_ext.vector_old.v_old
print 'It works.'

print 'envoke operator+ using new Boost.Python interface'
new = operators_ext.vector_new()
tmp = new + operators_ext.vector_new.v_new
print 'If you see this message than the bug was fixed. Thank you.'
