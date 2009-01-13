#pragma once
#include "libconfig.h"


struct EXPORT_SYMBOL rgbai{
    struct {
        float r,g,b,a;
    };
    int i;
};

struct EXPORT_SYMBOL color{
    union{
        struct {
            float r,g,b,a;
        };
        float val[4];
    };
};

struct {
    int x;
} unnamed_struct_with_mem_var_x;

void EXPORT_SYMBOL do_smth( color );

