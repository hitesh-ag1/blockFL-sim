import os

def create_ipfs_nodes(num_clients):
    for i in range(num_clients):
        node_init = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs init'
        api_ch = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs config Addresses.API /ip4/127.0.0.1/tcp/500'+str(i+2)
        gateway_ch = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs config Addresses.Gateway /ip4/127.0.0.1/tcp/808'+str(i+1)
        swarm = r"""[\"/ip4/0.0.0.0/tcp/400{}\", \"/ip6/::/tcp/400{}\"]""".format(str(i+2),str(i+2))
        swarm_ch = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs config --json Addresses.Swarm '+"\""+swarm+"\""
        rm_bootstrap = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs bootstrap rm --all'

        os.system(node_init)
        os.system(api_ch)
        os.system(gateway_ch)
        os.system(swarm_ch)
        os.system(rm_bootstrap)

    os.system("go get -u github.com/Kubuxu/go-ipfs-swarm-key-gen/ipfs-swarm-key-gen")
    os.system("~/go/bin/ipfs-swarm-key-gen > ~/.ipfs_fl0/swarm.key")

    peerid = (os.popen("IPFS_PATH=~/.ipfs_fl0 ipfs config  Identity.PeerID").read()).strip()
    ip = (os.popen("hostname -I").read()).strip()
    ip = ip.split(' ')[0]

    for i in range(1, num_clients):
        swarm_copy = 'cp ~/.ipfs_fl0/swarm.key ~/.ipfs_fl'+str(i)+'/swarm.key'
        os.system(swarm_copy)
    
    for i in range(num_clients):
        ip_peer = 'IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs bootstrap add /ip4/'+ip+'/tcp/4002/ipfs/'+peerid
        os.system(ip_peer)

    for i in range(num_clients):
        os.system("export LIBP2P_FORCE_PNET=1")
        os.system('IPFS_PATH=~/.ipfs_fl'+str(i)+' ipfs daemon &')