#pragma once

#include <memory>

namespace pof{

class __declspec(dllexport) number_t{
public:
	number_t();
	explicit number_t(int value);
	virtual ~number_t();
	virtual void print_it() const;
	int get_value() const;
	int get_value(){ return m_value; }
	void set_value(int x);

	number_t clone() const;
	std::auto_ptr<number_t> clone_ptr() const;
private:
	int m_value;
};

}
template class __declspec(dllexport) std::auto_ptr< pof::number_t >;

typedef std::auto_ptr< pof::number_t > number_aptr_t;

void __declspec(dllexport) do_smth( number_aptr_t& );

extern "C"{

int __declspec(dllexport) identity( int );

}

int __declspec(dllexport) identity_cpp( int );