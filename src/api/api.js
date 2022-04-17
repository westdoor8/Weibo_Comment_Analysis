import axios from 'axios';

let base = 'http://127.0.0.1:5000/api';

export const requestLogin = params => {
    return axios({
        method: 'POST',
        url: `${base}/login`,
        auth: params
    })
    .then(res => res.data);
};

export const setpwd = params => {
    return axios.post(`${base}/setpwd`, params);
};


export const getdrawPieChart = () => {
    return axios.get(`${base}/getdrawPieChart`);
};

export const getdrawLineChart = () => {
    return axios.get(`${base}/getdrawLineChart`);
};