from IR5G import *

anti_affinity_list = []
hyper = hypervisor()
dc_name = "datacenter_default"
hyper.add_datacenter(dc_name)
init_blade(hyper, dc_name)

eMBBvideo = slice(hyper, "eMBB Video")
eMBBvoice = slice(hyper, "eMBB Voice")

slices = [eMBBvideo, eMBBvoice]
slc = 0

def print_test():
    for s2 in slices:
        for key2, vnfs2 in s2.vnfs.items():
            print(vnfs2.name,vnfs2.vcpus/(vnfs2.scale_factor*pow(10,-4)))

def reset_blade(anti_affinity_list):
    for s in slices:
        s.subscribers = 0
        for k in s.vnfs:
            jj = len(s.vnfs[k].modules)
            for j in range(0,jj):
                s.vnfs[k].rmv_module(j,s.name+"#"+s.vnfs[k].name)
    del anti_affinity_list
    anti_affinity_list = []

def simulation_add_subscriber(new_subs, results_rr, mapping_rr, log_rr, vector):
    flag_affinity = vector[1]
    if new_subs < 0.8:
        eMBBvideo.add_subscriber()
        slc = 0
    else:
        eMBBvoice.add_subscriber()
        slc = 1
    for key, vnfs in slices[slc].vnfs.items():
        if slices[slc].subscribers > (vnfs.num_vcpus()/(vnfs.scale_factor*pow(10,-4))):
            i = len(vnfs.modules)
            flag_affinity = vector[1]
            for dd in hyper.datacenter:
                for bb in hyper.datacenter[dd]:
                    log_rr.write(f'{dd} {bb} {hyper.datacenter[dd][bb].resource} {hyper.datacenter[dd][bb].resources_clock()}\n')
            if(flag_affinity==1):
                flag_affinity = vnfs.add_module_rr_af(i,slices[slc].name+"#"+vnfs.name, anti_affinity_list)
                if(flag_affinity==0):
                    vector[1] = flag_affinity
                    log_rr.write("Affinity rule break\n")
                    log_rr.write(f'{slices[slc].name}_{key}#{i} {slices[slc].subscribers}  {(vnfs.num_vcpus()/(vnfs.scale_factor*pow(10,-4)))}\n')
                    slices[slc].subscribers = slices[slc].subscribers - 1
                    tot_subscribers = slices[0].subscribers + slices[1].subscribers
                    results_rr.write(f'{tot_subscribers}\t')

                    for s in slices:
                        results_rr.write(f'{s.subscribers}\t')
                        for k in s.vnfs:
                            results_rr.write(f'{len(s.vnfs[k].modules)}\t')
                    delta_cpu = hyper.best_free_resource('cpu') - hyper.worst_free_resource('cpu')
                    delta_ram = hyper.best_free_resource('ram') - hyper.worst_free_resource('ram')
                    delta_ssd = hyper.best_free_resource('ssd') - hyper.worst_free_resource('ssd')
                    used_res = hyper.sum_resources()
                    results_rr.write(f'{tot_cpu - used_res["cpu"]}\t{tot_ram - used_res["ram"]}\t{tot_ssd - used_res["ssd"]}\t{delta_cpu}\t{delta_ram}\t{delta_ssd}\t')

                    for d in hyper.datacenter:
                        for b in hyper.datacenter[d]:
                            used_resources = hyper.datacenter[d][b].resources_clock()
                            used_resources['cpu'] = used_resources['cpu'] - hyper.datacenter[d][b].resource['cpu']
                            used_resources['ram'] = used_resources['ram'] - hyper.datacenter[d][b].resource['ram']
                            used_resources['ssd'] = used_resources['ssd'] - hyper.datacenter[d][b].resource['ssd']
                            mapping_rr.write(f'{b}\t{hyper.datacenter[d][b].resource["cpu"]}\t{hyper.datacenter[d][b].resource["ram"]}\t{hyper.datacenter[d][b].resource["ssd"]}\t{used_resources["cpu"]}\t{used_resources["ram"]}\t{used_resources["ssd"]}\t')
                    for s2 in slices:
                        for key2, vnfs2 in s2.vnfs.items():
                            for var in vnfs2.modules:
                                mapping_rr.write(vnfs2.modules[var].guestname+"\t"+vnfs2.modules[var].hostname+"\t")
                    results_rr.write(slices[slc].name+"_"+vnfs.name+"#"+str(i)+"\t")
                    slices[slc].subscribers = slices[slc].subscribers + 1
                else:
                    log_rr.write(f'{slices[slc].name}_{key}#{i} - {vnfs.modules[slices[slc].name+"#"+vnfs.name+str(i)].hostname}\n')
                    vector[0] = 1
                    return
            if(flag_affinity==0):
                flag_affinity_resources = vnfs.add_module_rr_naf(i,slices[slc].name+"#"+vnfs.name, anti_affinity_list)
                if(flag_affinity_resources==0):
                    log_rr.write("No more resources\n")
                    log_rr.write(f'{slices[slc].name}_{key}#{i} {slices[slc].subscribers}  {(vnfs.num_vcpus()/(vnfs.scale_factor*pow(10,-4)))}\n')
                    slices[slc].subscribers = slices[slc].subscribers - 1
                    tot_subscribers = slices[0].subscribers + slices[1].subscribers
                    results_rr.write(f'{tot_subscribers}\t')
                    for s in slices:
                        results_rr.write(f'{s.subscribers}\t')
                        for k in s.vnfs:
                            results_rr.write(f'{len(s.vnfs[k].modules)}\t')
                    delta_cpu = hyper.best_free_resource('cpu') - hyper.worst_free_resource('cpu')
                    delta_ram = hyper.best_free_resource('ram') - hyper.worst_free_resource('ram')
                    delta_ssd = hyper.best_free_resource('ssd') - hyper.worst_free_resource('ssd')
                    used_res = hyper.sum_resources()
                    results_rr.write(f'{tot_cpu - used_res["cpu"]}\t{tot_ram - used_res["ram"]}\t{tot_ssd - used_res["ssd"]}\t{delta_cpu}\t{delta_ram}\t{delta_ssd}\t')
                    for d in hyper.datacenter:
                        for b in hyper.datacenter[d]:
                            used_resources = hyper.datacenter[d][b].resources_clock()
                            used_resources['cpu'] = used_resources['cpu'] - hyper.datacenter[d][b].resource['cpu']
                            used_resources['ram'] = used_resources['ram'] - hyper.datacenter[d][b].resource['ram']
                            used_resources['ssd'] = used_resources['ssd'] - hyper.datacenter[d][b].resource['ssd']
                            mapping_rr.write(f'{b}\t{hyper.datacenter[d][b].resource["cpu"]}\t{hyper.datacenter[d][b].resource["ram"]}\t{hyper.datacenter[d][b].resource["ssd"]}\t{used_resources["cpu"]}\t{used_resources["ram"]}\t{used_resources["ssd"]}\t')
                    for s2 in slices:
                        for key2, vnfs2 in s2.vnfs.items():
                            for var in vnfs2.modules:
                                mapping_rr.write(vnfs2.modules[var].guestname+"\t"+vnfs2.modules[var].hostname+"\t")
                    results_rr.write(slices[slc].name+"_"+vnfs.name+"#"+str(i)+"\n")
                    vector[0] = 0
                    return
                else:
                    log_rr.write(f'{slices[slc].name}_{key}#{i} - {vnfs.modules[slices[slc].name+"#"+vnfs.name+str(i)].hostname}\n')
                    vector[0] = 1
                    return