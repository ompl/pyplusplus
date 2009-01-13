#pragma once

#include "libconfig.h"

struct EXPORT_SYMBOL user_data_t{
    int i;
};


user_data_t* EXPORT_SYMBOL create();
int EXPORT_SYMBOL read_user_data(user_data_t*);
void EXPORT_SYMBOL destroy(user_data_t*);
