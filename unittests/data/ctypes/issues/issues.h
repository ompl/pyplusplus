#pragma once


struct __declspec(dllexport) return_by_value_t{
public:
    struct result_t{ int i; int j; int result; };
    result_t add( int i, int j ){
        result_t r = { i, j, i + j};
        return r;
    }
};

int __declspec(dllexport) add( int, int );
