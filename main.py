from IR5G import *
import simulation_rr as rr
import simulation_hg as hg
import simulation_vg as vg

high = random.randrange(8,11)
moderate = random.randrange(6,8)
low = random.randrange(4,6)
up_video = random.randrange(75,77)
up_voz = random.randrange(46,48)

slice_video_init(rr.eMBBvideo,up_video,high,moderate,low)
slice_voice_init(rr.eMBBvoice,up_voz,high,moderate,low)

slice_video_init(hg.eMBBvideo,up_video,high,moderate,low)
slice_voice_init(hg.eMBBvoice,up_voz,high,moderate,low)

slice_video_init(vg.eMBBvideo,up_video,high,moderate,low)
slice_voice_init(vg.eMBBvoice,up_voz,high,moderate,low)

run = 1
max_run = 1

rr_info = [1,1]
hg_info = [1,1]
vg_info = [1,1]

results_rr = open(f'RR/rr-results.txt', "w")
mapping_rr = open(f'RR/rr-mapping.txt', "w")
results_hg = open(f'HG/hg-results.txt', "w")
mapping_hg = open(f'HG/hg-mapping.txt', "w") 
results_vg = open(f'VG/vg-results.txt', "w")
mapping_vg = open(f'VG/vg-mapping.txt', "w")



while run <= max_run:
    loop_times = 0
    loop = 1
    log_rr = open(f'RR/rr-mapping#run{run}.txt', "w")
    log_hg = open(f'HG/hg-mapping#run{run}.txt', "w")
    log_vg = open(f'VG/vg-mapping#run{run}.txt', "w")
    rr_info[0] = 1
    hg_info[0] = 1
    vg_info[0] = 1
    rr_info[1] = 1
    hg_info[1] = 1
    vg_info[1] = 1
    print(f'Run#{run}')
    while loop:
        #print(rr_info[0] or hg_info[0] or vg_info[0], rr_info[0], hg_info[0], vg_info[0])
        new_subs = random.random()
        loop_times = loop_times + 1
        if rr_info[0]:
            rr.simulation_add_subscriber(new_subs,results_rr,mapping_rr,log_rr,rr_info)
        if hg_info[0]:
            hg.simulation_add_subscriber(new_subs,results_hg,mapping_hg,log_hg,hg_info)
        if vg_info[0]:
            vg.simulation_add_subscriber(new_subs,results_vg,mapping_vg,log_vg,vg_info)
        rr.print_test()
        exit(1)
        loop = rr_info[0] or hg_info[0] or vg_info[0]
    mapping_rr.write("\n")
    mapping_hg.write("\n")
    mapping_vg.write("\n")

    log_rr.close()
    log_hg.close()
    log_vg.close()
    rr.reset_blade(rr.anti_affinity_list)
    hg.reset_blade(hg.anti_affinity_list)
    vg.reset_blade(vg.anti_affinity_list, vg.vgreedy)
    
    high = random.randrange(8,11)
    moderate = random.randrange(6,8)
    low = random.randrange(4,6)
    up_video = random.randrange(75,77)
    up_voz = random.randrange(46,48)

    slice_video_sf_update(rr.eMBBvideo,up_video,high,moderate,low)
    slice_voice_sf_update(rr.eMBBvoice,up_voz,high,moderate,low)

    slice_video_sf_update(hg.eMBBvideo,up_video,high,moderate,low)
    slice_voice_sf_update(hg.eMBBvoice,up_voz,high,moderate,low)

    slice_video_sf_update(vg.eMBBvideo,up_video,high,moderate,low)
    slice_voice_sf_update(vg.eMBBvoice,up_voz,high,moderate,low)

    run = run+1