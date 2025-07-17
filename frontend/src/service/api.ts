import axios from 'axios';

const api = axios.create({
    baseURL: 'http://tower-jumps-alb-1691922525.us-east-1.elb.amazonaws.com',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;