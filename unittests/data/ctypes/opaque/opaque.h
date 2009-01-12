#pragma once

struct user_data_t{
    int i;
};


user_data_t* create();
int read_user_data(user_data_t*);
void destroy(user_data_t*);
