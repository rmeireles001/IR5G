anti_affinity_list = []
vgreedy = []
#Improvements to be done:
#   In line  print which resources are missing
import random

sys_ram = - 16
sys_cpu = - 8
sys_ssd = - 100

class cpu:
    def __init__(self, clock, n_cores):
        self.n_cores = n_cores
        self.core = clock
        self.threads = 2

 
class blade:
    def __init__(self, n_cpu, ram, n_ssd, n_interfaces, hostname):
        self.hostname = hostname
        self.n_cpu = n_cpu
        self.n_interfaces = n_interfaces
        self.ram = ram
        self.n_ssd = n_ssd
        self.cpus = []
        self.ssds = []
        self.interfaces = []
        self.active_vms = []
        self.resource = {'ram': 0, 'cpu': 0, 'ssd': 0}
        self.available_resources()
 
    def cpu_setup(self, clock, cores):
        if len(self.cpus) < self.n_cpu:
            self.cpus.append(cpu(clock, cores))
            self.available_resources()
        else:
            print("You cannot add more CPUs")
 
    def ssd_setup(self, capacity):
        if len(self.ssds) < self.n_ssd:
            self.ssds.append(capacity)
            self.available_resources()
        else:
            print("You cannot add more SSDs")

 
    def lst_blade(self):
        print("\nHostname: "+self.hostname+"\n-----------------------------------\n")
        print("Memory RAM\t"+str(self.ram))
        print("CPU\tNumber of Cores\t\tClock")
        i=1
        for element in self.cpus:
            print("CPU#"+str(i)+"\t"+str(element.n_cores)+"\t\t\t"+str(element.core))
            i=i+1
        print("SSD\tCapacity")
        i=1
        for element in self.ssds:
            print("SSD#"+str(i)+"\t"+str(element))
            i=i+1
        print("Interface\tMAC Address\t\t\tNetwork Address\t\tMask                   IP Address       Mask")
        i=1
        for element in self.interfaces:
            print("Interface#"+str(i)+"\t"+str(element.mac_addr)+"\t\t\t"+str(element.net_addr)+"\t\t"+str(element.net_mask)+"          "+str(element.ip_addr)+"         "+str(element.ip_mask))
            i=i+1
    def available_resources(self):
        sum_cpu = sys_cpu
        sum_ssd = sys_ssd
        for cpu in self.cpus:
            sum_cpu = sum_cpu + cpu.n_cores
        for ssd in self.ssds:
            sum_ssd = sum_ssd + ssd
        self.resource['ram'] = self.ram - sys_ram
        self.resource['cpu'] = sum_cpu
        self.resource['ssd'] = sum_ssd
    def resources_clock(self):
        sum_cpu = sys_cpu
        sum_ssd = sys_ssd
        for cpu in self.cpus:
            sum_cpu = sum_cpu + cpu.n_cores
        for ssd in self.ssds:
            sum_ssd = sum_ssd + ssd
        return {'ram': self.ram - sys_ram, 'cpu': sum_cpu, 'ssd': sum_ssd}
 
class hypervisor:
    def __init__(self):
        self.vms = {}
        self.datacenter = {}
        self.best_resource = {'ram': 0, 'cpu': 0, 'ssd': 0}
    def add_datacenter(self, name):
        self.datacenter[name] = {}
        self.vms[name] = {}
    def add_server(self, datacenter, host):
        if self.datacenter.get(datacenter) == None:
            print("Insert an existent datacenter name!")
        else:
            self.datacenter[datacenter][host.hostname] = host
            self.vms[datacenter][host.hostname] = {}
            new_vm_resources = host.resource
            if new_vm_resources['ram'] > self.best_resource['ram']:
                self.best_resource['ram'] = new_vm_resources['ram']
            if new_vm_resources['cpu'] > self.best_resource['cpu']:
                self.best_resource['cpu'] = new_vm_resources['cpu']
            if new_vm_resources['ssd'] > self.best_resource['ssd']:
                self.best_resource['ssd'] = new_vm_resources['ssd']
    def list_datacenter(self):
        for key, value in self.datacenter.items():
            print("Datacenter: ", key,"\n##########################")
            for k, host in value.items():
                print(host.lst_blade())

    def check_host(self, hostname, datacenter):
        if datacenter in self.datacenter:
            if hostname in self.datacenter[datacenter]:
                return 1
        return 0
    def check_vm(self, guestname, hostname, datacenter):
        if datacenter in self.vms:
            if hostname in self.vms[datacenter]:
                if guestname in self.vms[datacenter][hostname]:
                    return 1
        return 0
            
    def list_vms(self, datacenter, hostname):

        if self.datacenter.get(datacenter) == None:
            print("Insert an existent datacenter name!")
            return 0
        else:
            if self.check_host(hostname, datacenter) == 0:
                print("Insert an existent hostname!")
                return 0
        print("Datacenter: "+datacenter+" Host: "+hostname+"\n")
        for vm in self.vms[datacenter][hostname]:
            self.vms[datacenter][hostname][vm].lst_vm()

    def add_vm(self, n_cpu, core, clock, ram, storage, n_interfaces, guestname, hostname, datacenter):
        if self.datacenter.get(datacenter) == None:
            print("Insert an existent datacenter name!")
            return 0
        else:
            if not self.check_host(hostname, datacenter):
                print("Insert an existent hostname!")
                return 0
        vmm = self.datacenter[datacenter][hostname]
        if vmm.resource['ssd'] - storage < 0 :
            print("No enough storage in Host machine")
            exit(1)
        if n_cpu > vmm.n_cpu:
            print("Guest cannot have more CPUs than host")
            exit(1)
        if ram > vmm.ram:
            print("Guest cannot have more RAM than host")
            exit(1)
        sum_core = 0
        for i in range(0,vmm.n_cpu):
            sum_core = sum_core + vmm.cpus[i].n_cores
        if core > sum_core:
            print("Number of cores of virtual processor cannot be bigger than the number of cores from host's processor")
            exit(1)
        for i in range(0,n_cpu):
            if clock > vmm.cpus[i].core:
                print("Clock of virtual processor cannot be bigger than clock of host's processor")
                exit(1)
        new_vm = vm(n_cpu, ram, 1, 1, guestname, hostname, datacenter)
        for i in range(0, n_cpu):
            new_vm.cpu_setup(clock, core)
        new_vm.ssd_setup(storage)
        vmm.resource['ssd'] = vmm.resource['ssd'] - storage
        self.vms[datacenter][hostname][guestname] = new_vm

    def rmv_vm(self, guestname, hostname, datacenter):
        if not self.check_vm(guestname,hostname,datacenter):
            print("VM, Host or Datacenter inexistent")
            return 0
        host = self.datacenter[datacenter][hostname]
        vm = self.vms[datacenter][hostname][guestname]
        if vm.state==1:
            print("Backup and turn off your VM first")
        host.resource['ssd'] = host.resource['ssd'] + vm.ssds[0]
        for i in range(0,vm.n_ssd):
            del i
        for i in range(0,vm.n_cpu):
            del i
        del vm
        del self.vms[datacenter][hostname][guestname]

    def best_blade_af(self, cpu, ram, ssd, weight_cpu, weight_ram, weight_ssd, type, af):
        vmnames = []
        vmweights = []
        for key, value in self.datacenter.items():
            for key2, value2 in value.items():
                #print("->",key2,value2.resource)
                temp = value2.resource
                vmweights.append((temp['ram']/self.best_resource['ram'])*weight_ram+(temp['cpu']/self.best_resource['cpu'])*weight_cpu+(temp['ssd']/self.best_resource['ssd'])*weight_ssd)
                #vmweights.append((temp[0])*weight_ram+(temp[1])*weight_cpu+(temp[2])*weight_ssd)
                vmnames.append([key2,key])
        while vmnames:
            min_value = max(vmweights)
            vm_min = vmweights.index(min_value)
            vmnames[vm_min]
            if self.check_blade_resources(cpu,ram,ssd,vmnames[vm_min][0],vmnames[vm_min][1]) and self.affinity_check(type, af, vmnames[vm_min][1], vmnames[vm_min][0]):
                return vmnames[vm_min]
            else:
                vmweights.pop(vm_min)
                vmnames.pop(vm_min)
        return []
    
    def best_blade_naf(self, cpu, ram, ssd, weight_cpu, weight_ram, weight_ssd, type, af):
        vmnames = []
        vmweights = []
        for key, value in self.datacenter.items():
            for key2, value2 in value.items():
                #print("->",key2,value2.resource)
                temp = value2.resource
                vmweights.append((temp['ram']/self.best_resource['ram'])*weight_ram+(temp['cpu']/self.best_resource['cpu'])*weight_cpu+(temp['ssd']/self.best_resource['ssd'])*weight_ssd)
                #vmweights.append((temp[0])*weight_ram+(temp[1])*weight_cpu+(temp[2])*weight_ssd)
                vmnames.append([key2,key])
        while vmnames:
            min_value = max(vmweights)
            vm_min = vmweights.index(min_value)
            vmnames[vm_min]
            if self.check_blade_resources(cpu,ram,ssd,vmnames[vm_min][0],vmnames[vm_min][1]):
                return vmnames[vm_min]
            else:
                vmweights.pop(vm_min)
                vmnames.pop(vm_min)
        return []

    def best_blade_old(self, weight_cpu, weight_ram, weight_ssd):
        vmnames = []
        vmweights = []
        for key, value in self.datacenter.items():
            for key2, value2 in value.items():
                #print("->",key2,value2.resource)
                temp = value2.resource
                vmweights.append((temp['ram']/self.best_resource['ram'])*weight_ram+(temp['cpu']/self.best_resource['cpu'])*weight_cpu+(temp['ssd']/self.best_resource['ssd'])*weight_ssd)
                #vmweights.append((temp[0])*weight_ram+(temp[1])*weight_cpu+(temp[2])*weight_ssd)
                vmnames.append([key2,key])
        min_value = max(vmweights)
        vm_min = vmweights.index(min_value)
        return vmnames[vm_min]

    def powerOnVM(self, guestname, hostname, datacenter):
        if not self.check_host(hostname, datacenter):
            print("Enter with a valid datacenter or hostname!")
            return 0
        #self.vms[datacenter][hostname][guestname].state = 1
        resources = self.vms[datacenter][hostname][guestname].resources().copy()
        if self.datacenter[datacenter][hostname].resource['ram'] - resources[0] >= 0 and self.datacenter[datacenter][hostname].resource['cpu'] - resources[1] >= 0:
            self.vms[datacenter][hostname][guestname].state = 1
            self.datacenter[datacenter][hostname].resource['ram'] = self.datacenter[datacenter][hostname].resource['ram'] - resources[0]
            self.datacenter[datacenter][hostname].resource['cpu'] = self.datacenter[datacenter][hostname].resource['cpu'] - resources[1]
            self.datacenter[datacenter][hostname].active_vms.append([guestname, hostname, datacenter])
        else:
            print("You don't have enough available resources")
            #print which resources are missing

    def powerOffVM(self, guestname, hostname, datacenter):
        if not self.check_vm(guestname, hostname, datacenter):
            print("Enter with a valid datacenter or hostname!")
            return 0
        index = 0
        for i in self.datacenter[datacenter][hostname].active_vms:
            if i[0] == guestname and i[1] == hostname and i[2] == datacenter:
                del self.datacenter[datacenter][hostname].active_vms[index]
                break
            index = index + 1
        self.vms[datacenter][hostname][guestname].state = 0
        resources = self.vms[datacenter][hostname][guestname].resources().copy()
        self.datacenter[datacenter][hostname].resource['ram'] = self.datacenter[datacenter][hostname].resource['ram'] + resources[0]
        self.datacenter[datacenter][hostname].resource['cpu'] = self.datacenter[datacenter][hostname].resource['cpu'] + resources[1]
    def rr_affinity_list(self, type, affinity):
        list = []
        for key, value in self.datacenter.items():
            for k, host in value.items():
                affinity_var = 0
                for s in host.active_vms:
                    if self.vms[s[2]][s[1]][s[0]].type == type:
                        affinity_var = affinity_var+1
                if affinity_var < affinity:
                    list.append([k, key])
        return list
    
    def rr_list(self, list):
        for key, value in self.datacenter.items():
            for k, host in value.items():
                list.append([k, key])
        return list
    
    def affinity_check(self, type, affinity, dc, host):
        affinity_var = 0
        for s in self.datacenter[dc][host].active_vms:
            if self.vms[s[2]][s[1]][s[0]].type == type:
                affinity_var = affinity_var+1
        if affinity_var < affinity:
            return 1
        return 0
    
    def check_blade_resources(self, vcpus, ram, ssd, host, dc):
        resource_vector = self.datacenter[dc][host].resource
        if(ram > resource_vector['ram']):
            #print("Insufficient free RAM")
            return 0
        if(vcpus > resource_vector['cpu']):
            #print("Insufficient vCPUs available")
            return 0
        #print("The blade has available resources")
        return 1
    def worst_free_resource(self, param):
        worst = 100000000
        for key, value in self.datacenter.items():
            for k, host in value.items():
                if(host.resource[param]<worst):
                    worst = host.resource[param]
        return worst
    def best_free_resource(self, param):
        best = 0
        for key, value in self.datacenter.items():
            for k, host in value.items():
                if(host.resource[param]>best):
                    best = host.resource[param]
        return best
    def sum_resources(self):
        used_resources = {'cpu':0,'ram':0,'ssd':0}
        for key, value in self.datacenter.items():
            for k, host in value.items():
                used_resources['cpu'] = used_resources['cpu'] + host.resource['cpu']
                used_resources['ram'] = used_resources['ram'] + host.resource['ram']
                used_resources['ssd'] = used_resources['ssd'] + host.resource['ssd']
        return used_resources
    
class vm:
    def __init__(self, n_cpu, ram, n_ssd, n_interfaces, guestname, hostname, datacenter):
        self.datacenter = datacenter
        self.hostname = hostname
        self.guestname = guestname
        self.n_cpu = n_cpu
        self.n_interfaces = n_interfaces
        self.ram = ram
        self.n_ssd = n_ssd
        self.cpus = []
        self.ssds = []
        self.interfaces = []
        self.state = 0
        self.type = ""
 
    def cpu_setup(self, clock, cores):
        if len(self.cpus) < self.n_cpu:
            self.cpus.append(cpu(clock, cores))
        else:
            print("You cannot add more CPUs")
 
    def ssd_setup(self, capacity):
        if len(self.ssds) < self.n_ssd:
            self.ssds.append(capacity)
        else:
            print("You cannot add more SSDs")
 
    def lst_vm(self):
        print("Hostname: "+self.hostname)
        print("Guestname: "+self.guestname)
        print("State: "+str(self.state))
        print("Memory RAM\t"+str(self.ram))
        print("CPU\tNumber of Cores\t\tClock")
        i=1
        for element in self.cpus:
            print("CPU#"+str(i)+"\t"+str(element.n_cores)+"\t\t\t"+str(element.core))
            i=i+1
        print("SSD\tCapacity")
        i=1
        for element in self.ssds:
            print("SSD#"+str(i)+"\t"+str(element))
            i=i+1
        print("Interface\tMAC Address\t\t\tNetwork Address\t\tMask                   IP Address       Mask")
        i=1
        for element in self.interfaces:
            print("Interface#"+str(i)+"\t"+str(element.mac_addr)+"\t\t\t"+str(element.net_addr)+"\t\t"+str(element.net_mask)+"          "+str(element.ip_addr)+"         "+str(element.ip_mask))
            i=i+1
    def resources(self):
        sum_cpu = 0
        for cpu in self.cpus:
            sum_cpu = sum_cpu + cpu.n_cores
        return [self.ram, sum_cpu]
    def resources_clock(self):
        sum_cpu = 0
        sum_ssd = 0
        for cpu in self.cpus:
            sum_cpu = sum_cpu + cpu.n_cores
        for ssd in self.ssds:
            sum_ssd = sum_ssd + ssd
        return [self.ram, sum_cpu, sum_ssd]

class module:
    def __init__(self, id, type, guestname, hostname, datacenter):
        self.id = id
        self.type = type
        self.guestname = guestname
        self.hostname = hostname
        self.datacenter = datacenter


class vnf:
    def __init__(self, name, hypervisor):
        self.name = name
        self.modules = {}
        self.hypervisor = hypervisor
        self.vcpus = 0
        self.ram = 0
        self.ssd = 0
        self.wvcpus = 0
        self.wrap = 0
        self.wssd = 0
        self.anti_affinity = 0
        self.scale_factor = 0
    def add_module_rr_af(self, id, type, af_list):
        if(len(af_list)==0):
            #print(id, type)
            self.hypervisor.rr_list(af_list)
        flag_affinity = 1
        while(flag_affinity):
            if(af_list):
                host = af_list[0]
                af_list.pop(0)
                if(self.hypervisor.check_blade_resources(self.vcpus, self.ram, self.ssd, host[0], host[1]) and self.hypervisor.affinity_check(self.name, self.anti_affinity, host[1], host[0])):
                    self.modules[type+str(id)] = module(id, type, type+str(id), host[0], host[1])
                    clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                    self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                    self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                    self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                    #print(type+str(id)+" "+host[1]+" "+host[0]+" added by Round-Robin")
                    return 1
            else:
                flag_affinity = 0
        #print("Impossible to allocate according to this Anti-Affinity policy")
        return 0
    def add_module_rr_naf(self, id, type, af_list):
        if(len(af_list)==0):
            #print(id, type)
            self.hypervisor.rr_list(af_list)
        flag_affinity = 1
        while(flag_affinity):
            if(af_list):
                host = af_list[0]
                af_list.pop(0)
                if(self.hypervisor.check_blade_resources(self.vcpus, self.ram, self.ssd, host[0], host[1])):
                    self.modules[type+str(id)] = module(id, type, type+str(id), host[0], host[1])
                    clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                    self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                    self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                    self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                    #print(type+str(id)+" "+host[1]+" "+host[0]+" added by Round-Robin")
                    return 1
            else:
                flag_affinity = 0
        print("Impossible to allocate according to this Anti-Affinity policy")
        return 0
    def add_module_greedy_naf(self, id, type):
        host = self.hypervisor.best_blade_old(self.wvcpus,self.wvcpus,self.wssd)
        if(self.hypervisor.check_blade_resources(self.vcpus, self.ram, self.ssd, host[0], host[1])):
            self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
            clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
            self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
            self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
            self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
            #print(type+str(id)+" "+host[1]+" "+host[0]+" added by Greedy Selection")
            return 1
        print("No free resources for the most available host")
        return 0
    
    def add_module_greedy_af(self, id, type):
        host = self.hypervisor.best_blade_af(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity)
        if(host):
            self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
            clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
            self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
            self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
            self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
            #print(type+str(id)+" "+host[1]+" "+host[0]+" added by Greedy Selection")
            return 1
        print("No free resources for the most available host")
        return 0

    def add_module_vgreedy_af(self, id, type, vgreedy):
        flag = 1

        if(len(vgreedy)==0):
            host = self.hypervisor.best_blade_af(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity)
            if(host):
                vgreedy.append(host[0])
                vgreedy.append(host[1])
                self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                return 1
        else:
            host = vgreedy
            if(self.hypervisor.check_blade_resources(self.vcpus, self.ram, self.ssd, host[0], host[1]) and self.hypervisor.affinity_check(self.name, self.anti_affinity, host[1], host[0])):
                self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                return 1
            else:
                vgreedy.pop(0)
                vgreedy.pop(0)
                host = self.hypervisor.best_blade_af(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity)
                if(host):
                    vgreedy.append(host[0])
                    vgreedy.append(host[1])
                    self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                    clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                    self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                    self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                    self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                    return 1
        return 0
    
    def add_module_vgreedy_naf(self, id, type, vgreedy):
        flag = 1
        if(len(vgreedy)==0):
            host = self.hypervisor.best_blade_naf(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity)
            if(host):
                vgreedy.append(host[0])
                vgreedy.append(host[1])
                self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                return 1
        else:
            host = vgreedy
            if(self.hypervisor.check_blade_resources(self.vcpus, self.ram, self.ssd, host[0], host[1])):
                self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                return 1
            else:
                vgreedy.pop(0)
                vgreedy.pop(0)
                host = self.hypervisor.best_blade_naf(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity)
                if(host):
                    vgreedy.append(host[0])
                    vgreedy.append(host[1])
                    self.modules[type+str(id)] = module(id, self.name, type+str(id), host[0], host[1])
                    clock = self.hypervisor.datacenter[host[1]][host[0]].cpus[0].core
                    self.hypervisor.add_vm(1,self.vcpus,clock,self.ram,self.ssd,1,type+str(id), host[0], host[1])
                    self.hypervisor.powerOnVM(type+str(id), host[0], host[1])
                    self.hypervisor.vms[host[1]][host[0]][type+str(id)].type = type
                    return 1
        return 0
                    

        #while flag:
        #    if(len(self.anti_affinity_list)==0):
        #        self.anti_affinity_list.append(self.hypervisor.best_blade_af(self.vcpus, self.ram, self.ssd, self.wvcpus,self.wvcpus,self.wssd, self.name, self.anti_affinity))
        #        flag = 0
        #    if

    def rmv_module(self, id, type):
        m = self.modules[type+str(id)]
        self.hypervisor.powerOffVM(m.guestname, m.hostname, m.datacenter)
        self.hypervisor.rmv_vm(m.guestname, m.hostname, m.datacenter)
        del m
        del self.modules[type+str(id)]
    
    def num_vcpus(self):
        return len(self.modules)*self.vcpus
    
    def config_params(self, vcpus, ram, ssd, wvcpus, wrap, wssd, anti_affinity, scale_factor):
        self.vcpus = vcpus
        self.ram = ram
        self.ssd = ssd
        self.wvcpus = wvcpus
        self.wrap = wrap
        self.wssd = wssd
        self.anti_affinity = anti_affinity
        self.scale_factor = scale_factor



class slice:
    def __init__(self, hypervisor, name):
        self.vnfs = {}
        self.hypervisor = hypervisor
        self.subscribers = 0
        self.name = name
    def add_vnf(self, name):
        vnff = vnf(name, self.hypervisor)
        self.vnfs[name] = vnff
    def list_vnfs(self):
        for s in self.vnfs:
            print(self.vnfs[s].name)
    def add_subscriber(self):
        self.subscribers = self.subscribers + 1 

def init_blade(hyper, dc):
    for i in range(0,20):
        blade_tmp = blade(2,768,2,10,"host#"+str(i+1))
        blade_tmp.cpu_setup(2.7, 28)
        blade_tmp.cpu_setup(2.7, 28)
        blade_tmp.ssd_setup(10240)
        hyper.add_server(dc,blade_tmp)

def slice_video_init(eMBBvideo, up, high, moderate, low):
    eMBBvideo.add_vnf('AMF')
    eMBBvideo.vnfs['AMF'].config_params(6,6,12,7,3,1,af,high)
    eMBBvideo.add_vnf('SMF')
    eMBBvideo.vnfs['SMF'].config_params(6,6,12,7,7,3,af,high)
    eMBBvideo.add_vnf('UPF')
    eMBBvideo.vnfs['UPF'].config_params(48,78,168,5,5,1,af,up)
    eMBBvideo.add_vnf('PCF')
    eMBBvideo.vnfs['PCF'].config_params(3,6,12,5,3,3,af,moderate)
    eMBBvideo.add_vnf('UDM')
    eMBBvideo.vnfs['UDM'].config_params(12,24,60,3,5,1,af,low)
    eMBBvideo.add_vnf('AF')
    eMBBvideo.vnfs['AF'].config_params(12,24,24,3,3,1,af,low)
    eMBBvideo.add_vnf('NEF')
    eMBBvideo.vnfs['NEF'].config_params(6,6,12,3,3,1,af,low)
    eMBBvideo.add_vnf('AUSF')
    eMBBvideo.vnfs['AUSF'].config_params(12,24,60,5,3,3,af,moderate)
    eMBBvideo.add_vnf('NSSF')
    eMBBvideo.vnfs['NSSF'].config_params(6,6,12,3,3,1,af,low)
    eMBBvideo.add_vnf('NRF')
    eMBBvideo.vnfs['NRF'].config_params(6,6,12,5,5,7,af,moderate)

def slice_voice_init(eMBBvoice, up, high, moderate, low):
    eMBBvoice.add_vnf('AMF')
    eMBBvoice.vnfs['AMF'].config_params(6,6,12,5,3,1,af,moderate)
    eMBBvoice.add_vnf('SMF')
    eMBBvoice.vnfs['SMF'].config_params(6,6,12,5,5,3,af,moderate)
    #eMBBvoice.add_vnf('UPF')
    #eMBBvoice.vnfs['UPF'].config_params(30,54,72,3,3,3,af,low)
    eMBBvoice.add_vnf('UPF')
    eMBBvoice.vnfs['UPF'].config_params(30,54,72,3,3,3,af,up)
    eMBBvoice.add_vnf('PCF')
    eMBBvoice.vnfs['PCF'].config_params(3,6,12,5,3,3,af,moderate)
    eMBBvoice.add_vnf('UDM')
    eMBBvoice.vnfs['UDM'].config_params(12,24,60,3,5,7,af,low)
    eMBBvoice.add_vnf('AUSF')
    eMBBvoice.vnfs['AUSF'].config_params(12,24,60,5,3,3,af,moderate)
    eMBBvoice.add_vnf('NSSF')
    eMBBvoice.vnfs['NSSF'].config_params(6,6,12,3,3,1,af,low)
    eMBBvoice.add_vnf('NRF')
    eMBBvoice.vnfs['NRF'].config_params(6,6,12,3,5,7,af,low)

def slice_video_sf_update(eMBBvideo, up, high, moderate, low):
    eMBBvideo.vnfs['AMF'].scale_factor = high
    eMBBvideo.vnfs['SMF'].scale_factor = high
    eMBBvideo.vnfs['UPF'].scale_factor = up
    eMBBvideo.vnfs['PCF'].scale_factor = moderate
    eMBBvideo.vnfs['UDM'].scale_factor = low
    eMBBvideo.vnfs['AF'].scale_factor = moderate
    eMBBvideo.vnfs['NEF'].scale_factor = low
    eMBBvideo.vnfs['AUSF'].scale_factor = moderate
    eMBBvideo.vnfs['NSSF'].scale_factor = low
    eMBBvideo.vnfs['NRF'].scale_factor = moderate

def slice_voice_sf_update(eMBBvoice, up, high, moderate, low):
    eMBBvoice.vnfs['AMF'].scale_factor = high
    eMBBvoice.vnfs['SMF'].scale_factor = high
    eMBBvoice.vnfs['UPF'].scale_factor = up
    eMBBvoice.vnfs['PCF'].scale_factor = moderate
    eMBBvoice.vnfs['UDM'].scale_factor = low
    eMBBvoice.vnfs['AUSF'].scale_factor = moderate
    eMBBvoice.vnfs['NSSF'].scale_factor = low
    eMBBvoice.vnfs['NRF'].scale_factor = low

def print_scale_factor(slices, log):
    for s in slices:
        for key, vnfss in s.vnfs.items():
               log.write(f'{s.name} {key} {vnfss.scale_factor}\n')
               print(s.name, key, vnfss.scale_factor)

af = 1
tot_cpu = 960
tot_ram = 15680
tot_ssd = 202800
