#ifndef __transfer_ownership_to_be_exported_hpp__
#define __transfer_ownership_to_be_exported_hpp__

struct event_t
{
    virtual void notify() = 0;
    virtual ~event_t(){}
};

struct do_nothing_t : event_t{
    virtual void notify(){};
};

struct simulator_t{
    
    void schedule(event_t *event) {
        m_event = event;
    };

    void run() {
        m_event->notify();
        delete m_event;
        m_event = 0;
    };

private:
    event_t* m_event;
};


#endif//__transfer_ownership_to_be_exported_hpp__
