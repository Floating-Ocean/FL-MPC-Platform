import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import locale from 'element-plus/es/locale/lang/zh-cn';

import axios from 'axios'

import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
dayjs.extend(utc)

axios.defaults.baseURL = 'http://127.0.0.1:5000';
axios.defaults.withCredentials = true;

const app = createApp(App);
app.config.globalProperties.$ajax = axios;

app.use(router)
app.use(ElementPlus, {locale})

app.mount('#app');

