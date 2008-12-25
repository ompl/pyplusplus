"""
The "data" dictionary was generate dusing the following code:


import pprint
from pygccxml.msvc import mspdb
from pygccxml import declarations
from pygccxml.msvc import common_utils as msvc_utils

pdb_file = r'E:\development\language-binding\pyplusplus_dev\pyplusplus\cpptypes\mydll\release\mydll.pdb'

reader = mspdb.decl_loader_t( pdb_file )
opt = mspdb.enums.UNDECORATE_NAME_OPTIONS.UNDNAME_SCOPES_ONLY

d = {}
for smbl in reader.public_symbols.itervalues():
    name = smbl.name
    undecorated_name = smbl.get_undecoratedNameEx(opt)
    d[ name ] = undecorated_name
    d[ undecorated_name ] = name

pprint.pprint( d )


Obviously the result is too big and some additional work should be done.
"""

data = {u'??$?6U?$char_traits@D@std@@@std@@YAAAV?$basic_ostream@DU?$char_traits@D@std@@@0@AAV10@PBD@Z': u'std::basic_ostream<char,std::char_traits<char> > & std::operator<<<std::char_traits<char> >(std::basic_ostream<char,std::char_traits<char> > &,char const *)',
 u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@AAV01@@Z': u'std::auto_ptr<number_t>::auto_ptr<number_t>(std::auto_ptr<number_t> &)',
 u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@PAVnumber_t@@@Z': u'std::auto_ptr<number_t>::auto_ptr<number_t>(number_t *)',
 u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@U?$auto_ptr_ref@Vnumber_t@@@1@@Z': u'std::auto_ptr<number_t>::auto_ptr<number_t>(std::auto_ptr_ref<number_t>)',
 u'??0number_t@@QAE@ABV0@@Z': u'number_t::number_t(number_t const &)',
 u'??0number_t@@QAE@H@Z': u'number_t::number_t(int)',
 u'??0number_t@@QAE@XZ': u'number_t::number_t(void)',
 u'??0sentry@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@AAV12@@Z': u'std::basic_ostream<char,std::char_traits<char> >::sentry::sentry(std::basic_ostream<char,std::char_traits<char> > &)',
 u'??1?$auto_ptr@Vnumber_t@@@std@@QAE@XZ': u'std::auto_ptr<number_t>::~auto_ptr<number_t>(void)',
 u'??1_Sentry_base@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@XZ': u'std::basic_ostream<char,std::char_traits<char> >::_Sentry_base::~_Sentry_base(void)',
 u'??1number_t@@UAE@XZ': u'number_t::~number_t(void)',
 u'??1sentry@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@XZ': u'std::basic_ostream<char,std::char_traits<char> >::sentry::~sentry(void)',
 u'??2@YAPAXI@Z': u'void * operator new(unsigned int)',
 u'??3@YAXPAX@Z': u'void operator delete(void *)',
 u'??4?$auto_ptr@Vnumber_t@@@std@@QAEAAV01@AAV01@@Z': u'std::auto_ptr<number_t> & std::auto_ptr<number_t>::operator=(std::auto_ptr<number_t> &)',
 u'??4?$auto_ptr@Vnumber_t@@@std@@QAEAAV01@U?$auto_ptr_ref@Vnumber_t@@@1@@Z': u'std::auto_ptr<number_t> & std::auto_ptr<number_t>::operator=(std::auto_ptr_ref<number_t>)',
 u'??4number_t@@QAEAAV0@ABV0@@Z': u'number_t & number_t::operator=(number_t const &)',
 u'??C?$auto_ptr@Vnumber_t@@@std@@QBEPAVnumber_t@@XZ': u'number_t * std::auto_ptr<number_t>::operator->(void)',
 u'??D?$auto_ptr@Vnumber_t@@@std@@QBEAAVnumber_t@@XZ': u'number_t & std::auto_ptr<number_t>::operator*(void)',
 u'??_Enumber_t@@UAEPAXI@Z': u"void * number_t::`vector deleting destructor'(unsigned int)",
 u'??_F?$auto_ptr@Vnumber_t@@@std@@QAEXXZ': u"void std::auto_ptr<number_t>::`default constructor closure'(void)",
 u'??_M@YGXPAXIHP6EX0@Z@Z': u"void `eh vector destructor iterator'(void *,unsigned int,int,void (*)(void *))",
 u'??_V@YAXPAX@Z': u'void operator delete[](void *)',
 u'?clone@number_t@@QBE?AV1@XZ': u'number_t number_t::clone(void)',
 u'?clone_ptr@number_t@@QBE?AV?$auto_ptr@Vnumber_t@@@std@@XZ': u'std::auto_ptr<number_t> number_t::clone_ptr(void)',
 u'?get@?$auto_ptr@Vnumber_t@@@std@@QBEPAVnumber_t@@XZ': u'number_t * std::auto_ptr<number_t>::get(void)',
 u'?get_value@number_t@@QBEHXZ': u'int number_t::get_value(void)',
 u'?print_it@number_t@@QBEXXZ': u'void number_t::print_it(void)',
 u'?release@?$auto_ptr@Vnumber_t@@@std@@QAEPAVnumber_t@@XZ': u'number_t * std::auto_ptr<number_t>::release(void)',
 u'?reset@?$auto_ptr@Vnumber_t@@@std@@QAEXPAVnumber_t@@@Z': u'void std::auto_ptr<number_t>::reset(number_t *)',
 u'?set_value@number_t@@QAEXH@Z': u'void number_t::set_value(int)',
 u'?terminate@@YAXXZ': u'void terminate(void)',
 u'_DllMain@12': u'_DllMain@12',
 u'_atexit': u'_atexit',
 u'int number_t::get_value(void)': u'?get_value@number_t@@QBEHXZ',
 u'number_t & number_t::operator=(number_t const &)': u'??4number_t@@QAEAAV0@ABV0@@Z',
 u'number_t & std::auto_ptr<number_t>::operator*(void)': u'??D?$auto_ptr@Vnumber_t@@@std@@QBEAAVnumber_t@@XZ',
 u'number_t * std::auto_ptr<number_t>::get(void)': u'?get@?$auto_ptr@Vnumber_t@@@std@@QBEPAVnumber_t@@XZ',
 u'number_t * std::auto_ptr<number_t>::operator->(void)': u'??C?$auto_ptr@Vnumber_t@@@std@@QBEPAVnumber_t@@XZ',
 u'number_t * std::auto_ptr<number_t>::release(void)': u'?release@?$auto_ptr@Vnumber_t@@@std@@QAEPAVnumber_t@@XZ',
 u'number_t number_t::clone(void)': u'?clone@number_t@@QBE?AV1@XZ',
 u'number_t::number_t(int)': u'??0number_t@@QAE@H@Z',
 u'number_t::number_t(number_t const &)': u'??0number_t@@QAE@ABV0@@Z',
 u'number_t::number_t(void)': u'??0number_t@@QAE@XZ',
 u'number_t::~number_t(void)': u'??1number_t@@UAE@XZ',
 u'std::auto_ptr<number_t> & std::auto_ptr<number_t>::operator=(std::auto_ptr<number_t> &)': u'??4?$auto_ptr@Vnumber_t@@@std@@QAEAAV01@AAV01@@Z',
 u'std::auto_ptr<number_t> & std::auto_ptr<number_t>::operator=(std::auto_ptr_ref<number_t>)': u'??4?$auto_ptr@Vnumber_t@@@std@@QAEAAV01@U?$auto_ptr_ref@Vnumber_t@@@1@@Z',
 u'std::auto_ptr<number_t> number_t::clone_ptr(void)': u'?clone_ptr@number_t@@QBE?AV?$auto_ptr@Vnumber_t@@@std@@XZ',
 u'std::auto_ptr<number_t>::auto_ptr<number_t>(number_t *)': u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@PAVnumber_t@@@Z',
 u'std::auto_ptr<number_t>::auto_ptr<number_t>(std::auto_ptr<number_t> &)': u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@AAV01@@Z',
 u'std::auto_ptr<number_t>::auto_ptr<number_t>(std::auto_ptr_ref<number_t>)': u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@U?$auto_ptr_ref@Vnumber_t@@@1@@Z',
 u'std::auto_ptr<number_t>::~auto_ptr<number_t>(void)': u'??1?$auto_ptr@Vnumber_t@@@std@@QAE@XZ',
 u'std::basic_ostream<char,std::char_traits<char> > & std::operator<<<std::char_traits<char> >(std::basic_ostream<char,std::char_traits<char> > &,char const *)': u'??$?6U?$char_traits@D@std@@@std@@YAAAV?$basic_ostream@DU?$char_traits@D@std@@@0@AAV10@PBD@Z',
 u'std::basic_ostream<char,std::char_traits<char> >::_Sentry_base::~_Sentry_base(void)': u'??1_Sentry_base@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@XZ',
 u'std::basic_ostream<char,std::char_traits<char> >::sentry::sentry(std::basic_ostream<char,std::char_traits<char> > &)': u'??0sentry@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@AAV12@@Z',
 u'std::basic_ostream<char,std::char_traits<char> >::sentry::~sentry(void)': u'??1sentry@?$basic_ostream@DU?$char_traits@D@std@@@std@@QAE@XZ',
 u"void * number_t::`vector deleting destructor'(unsigned int)": u'??_Enumber_t@@UAEPAXI@Z',
 u'void * operator new(unsigned int)': u'??2@YAPAXI@Z',
 u"void `eh vector destructor iterator'(void *,unsigned int,int,void (*)(void *))": u'??_M@YGXPAXIHP6EX0@Z@Z',
 u'void number_t::print_it(void)': u'?print_it@number_t@@QBEXXZ',
 u'void number_t::set_value(int)': u'?set_value@number_t@@QAEXH@Z',
 u'void operator delete(void *)': u'??3@YAXPAX@Z',
 u'void operator delete[](void *)': u'??_V@YAXPAX@Z',
 u"void std::auto_ptr<number_t>::`default constructor closure'(void)": u'??_F?$auto_ptr@Vnumber_t@@@std@@QAEXXZ',
 u'void std::auto_ptr<number_t>::reset(number_t *)': u'?reset@?$auto_ptr@Vnumber_t@@@std@@QAEXPAVnumber_t@@@Z',
 u'void terminate(void)': u'?terminate@@YAXXZ'
}


ddd

