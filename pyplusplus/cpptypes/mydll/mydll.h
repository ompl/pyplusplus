#pragma once

#include <memory>

class __declspec(dllexport) number_t{
public:
	number_t();
	explicit number_t(int value);
	virtual ~number_t();
	void print_it() const;
	int get_value() const;
	void set_value(int x);

	number_t clone() const;
	std::auto_ptr<number_t> clone_ptr() const;
private:
	int m_value;
};

template class __declspec(dllexport) std::auto_ptr< number_t >;
