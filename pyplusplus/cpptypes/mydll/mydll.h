#pragma once

class __declspec(dllexport) number_t{
public:
	number_t();
	explicit number_t(int value);
	virtual ~number_t();
	void print_it() const;
	int get_value() const;
	void set_value(int x);

	number_t clone() const;

private:
	int m_value;
};

