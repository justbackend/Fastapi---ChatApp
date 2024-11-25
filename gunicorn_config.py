bind = 'unix:/home/mobile-lorry/mobile-lorry.sock'
workers = 8
worker_class = 'uvicorn.workers.UvicornWorker'
forwarded_allow_ips = '*'