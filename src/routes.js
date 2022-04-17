import Login from './views/Login.vue'
import NotFound from './views/404.vue'
import Home from './views/Home.vue'
import UsersTable from './views/nav1/UserListTable.vue'
import echarts from './views/charts/echarts.vue'
import WeiboTable from './views/nav1/WeiboListTable'

let routes = [
    {
        path: '/login',
        component: Login,
        name: '',
        hidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true
    },
    //{ path: '/main', component: Main },
    {
        path: '/',
        component: Home,
        name: 'Table',
        leaf: true,//只有一个节点
        iconCls: 'fa fa-id-card-o',//图标样式class
        children: [
            { path: '/users_table', component: UsersTable, name: '用户信息' },
        ]
    },
        {
        path: '/',
        component: Home,
        name: 'Table',
        leaf: true,//只有一个节点
        iconCls: 'fa fa-id-card-o',//图标样式class
        children: [
            { path: '/weibos_table', component: WeiboTable, name: '微博信息' },
        ]
    },
    {
        path: '/',
        component: Home,
        name: 'Charts',
        leaf: true,
        iconCls: 'fa fa-bar-chart',
        children: [
            { path: '/echarts', component: echarts, name: '图表展示' }
        ]
    },
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    }
];

export default routes;