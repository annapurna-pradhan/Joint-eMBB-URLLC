class Scheduler():
    """Base class for scheduler.
    
    """

    def __init__(self, RB_map, users):
        self.RB_map = RB_map
        self.users = users
    
    def allocate_resource(self):
        self._user_sort()
        raise NotImplementedError

    def _user_sort(self):
        user_indexes = list(range(0, len(self.users)))
        return user_indexes


class PfScheduler(Scheduler):
    """Scheduler for embb users at the beginning of each embb time slot.
       
       Calculate the weights of each user, sort and assign one by one 
       until the rb units are all assigned, assign the embb user requesting 
       more rbs with superiority. #TODO right???

       Assign rb from the very beginning of the RB map every scheduling.
    """

    def __init__(self, RB_map, users):
        Scheduler.__init__(self, RB_map, users)
        self.pf_weight = []
        self.user_indexes = []
    
    def allocate_resource(self):
        self._user_sort()
        rb_current = self.RB_map.rb_avi
        rb_start = 0
        for i in self.user_indexes:
            embb_user = self.users[i]
            if embb_user.active == 0:
                print ("ERROR: Inactive embb user is not clear!")
                continue
            if rb_current >= embb_user.rb_num_req:
                embb_user.rb_num_ass = embb_user.rb_num_req
                embb_user.rate_avg = (embb_user.rate_avg * embb_user.sche_times + embb_user.DRC) / (embb_user.sche_times + 1)
                embb_user.rate_cur = embb_user.DRC
                embb_user.sche_times += 1
                embb_user.rb_start = rb_start
                self.RB_map.bitmap[rb_start:embb_user.rb_num_req+rb_start] = int(embb_user.user_info['id'])
                rb_start += embb_user.rb_num_ass
                rb_current -= embb_user.rb_num_req
            else:
                embb_user.rb_num_ass = rb_current
                new_DRC = (rb_current * embb_user.rb_size / 1000) / embb_user.slot_len
                embb_user.rate_avg = (embb_user.rate_avg * embb_user.sche_times + new_DRC) / (embb_user.sche_times + 1)
                embb_user.rate_cur = new_DRC
                embb_user.sche_times += 1
                embb_user.rb_start = rb_start
                self.RB_map.bitmap[rb_start:rb_current+rb_start] = int(embb_user.user_info['id'])
                break
        
    def _user_sort(self):
        self.pf_weight = []
        pf_weight = []
        zero_flag = True
        for i in self.users:
            weighti = i.DRC / (0.01 * i.DRC + 0.99 * i.rate_avg)
            if i.rate_avg > 0:
                zero_flag = False
            self.pf_weight.append(weighti)
            pf_weight.append(weighti * i.DRC)
        if zero_flag is False:
            pf_weight = self.pf_weight
        self.user_indexes = [index for index, value in sorted(list(enumerate(pf_weight)),key=lambda x:x[1],reverse = True)]
        
