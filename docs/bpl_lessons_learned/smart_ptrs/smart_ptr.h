#ifndef smart_ptr_t_19_09_2006
#define smart_ptr_t_19_09_2006

#include <assert.h>

template<class T> class smart_ptr_t {
protected:
    T* pRep;
    unsigned int* pUseCount;
public:

    smart_ptr_t()
    : pRep(0), pUseCount(0)
    {}

    //What will happen if rep is NULL? -> bug
    explicit smart_ptr_t(T* rep)
    : pRep(rep), pUseCount( new unsigned int(1) )
    {}

    smart_ptr_t(const smart_ptr_t& r)
    : pRep(0), pUseCount(0)
    {
        pRep = r.get();
        pUseCount = r.useCountPointer();
        if(pUseCount){
            ++(*pUseCount);
        }
    }

    smart_ptr_t& operator=(const smart_ptr_t& r){
        if( pRep == r.pRep ){
            return *this;
        }

        release();

        pRep = r.get();
        pUseCount = r.useCountPointer();
        if(pUseCount){
            ++(*pUseCount);
        }
        return *this;
    }


    template<class Y>
    smart_ptr_t(const smart_ptr_t<Y>& r)
    : pRep(0), pUseCount(0)
    {
        pRep = r.get();
        pUseCount = r.useCountPointer();
        if(pUseCount){
            ++(*pUseCount);
        }
    }

    template< class Y>
    smart_ptr_t& operator=(const smart_ptr_t<Y>& r){
        if( pRep == r.pRep ){
            return *this;
        }

        release();

        pRep = r.get();
        pUseCount = r.useCountPointer();
        if(pUseCount){
            ++(*pUseCount);
        }
        return *this;
    }

    virtual ~smart_ptr_t() {
        release();
    }

    inline T& operator*() const {
        assert(pRep); return *pRep;
    }

    inline T* operator->() const {
        assert(pRep); return pRep;
    }

    inline T* get() const {
        return pRep;
    }

    inline unsigned int* useCountPointer() const {
        return pUseCount;
    }

    inline T* getPointer() const {
        return pRep;
    }

protected:

    inline void release(void){
        bool destroyThis = false;

        if( pUseCount ){
            if( --(*pUseCount) == 0){
                destroyThis = true;
            }
        }
        if (destroyThis){
            destroy();
        }
    }

    virtual void destroy(void){
        delete pRep;
        delete pUseCount;
    }
};


#endif //smart_ptr_t_19_09_2006

