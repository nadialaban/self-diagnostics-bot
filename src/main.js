import Vue from 'vue'
import App from './App.vue'
import axios from "axios";
import VueConfirmDialog from 'vue-confirm-dialog'
import vmodal from 'vue-js-modal'

window.Event = new class {
    constructor() {
        this.vue = new Vue();
    }

    fire(event, data = null) {
        if (!data && data !== 0) {
            console.log('sending event', event);
        } else {
            console.log('sending event', event, 'with data', data);
        }

        this.vue.$emit(event, data);
    }

    listen(event, callback) {
        this.vue.$on(event, callback);
    }
};

Vue.mixin({
    methods: {
        url: function (action) {
            let api_host = window.API_HOST;
            let agent_token = window.AGENT_TOKEN;
            let contract_id = window.CONTRACT_ID;
            let agent_id = window.AGENT_ID;

            return api_host + '/api/client/agents/' + agent_id + '/?action=' + action + '&contract_id=' + contract_id + '&agent_token=' + agent_token
        },
        img_url: function (color, name) {
            return window.LOCAL_HOST + '/static/icons/' + color + '/icons8-' + name + '-100.png'
        },
        empty: function (e) {
            return !e && e !== 0
        },
        get_algorithm: function (algorithm_id) {
            let alg = null
            this.axios.get(this.url('/api/algorithm/' + algorithm_id))
                .then(response => alg = response).catch(this.process_load_error);
            return alg
        },
        get_empty_algorithm: function () {
            return {
                'id': null,
                'creator': window.CLINIC_ID,
                'title': '',
                'icon': '',
                'patient_description': '',
                'doctor_description': '',
                'keywords': '',
                'depended_algorithms': [],
                'depends': false,
                'questions': [this.get_empty_question(1)],
                'results': [this.get_empty_result(1)]
            }
        },
        get_empty_question: function (question_id) {
            return {
                'id': question_id,
                'description': '',
                'answers': [
                    {
                        'answer': 'Да',
                        'next_state': ''
                    },
                    {
                        'answer': 'Нет',
                        'next_state': ''
                    }
                ],
                'icon': ''
            }
        },
        get_empty_result: function (result_id) {
            return {
                'id': result_id,
                'title': '',
                'description': '',
                'color': '',
                'need_warn': false,
                'need_response': false,
                'message': '',
                'icon': ''
            }
        },
        get_algorithms: function () {
            let algs = null
            this.axios.get(this.url('/api/algorithms'))
                .then(response => algs = response).catch(this.process_load_error);
            return algs
        },
        get_enabled_algorithms: function () {
            let algs = null
            this.axios.get(this.url('/api/enabled_algorithms'))
                .then(response => algs = response).catch(this.process_load_error);
            return algs
        },
        get_icons: function () {
            let icons = null
            this.axios.get(this.url('/api/icons'))
                .then(response => icons = response).catch(this.process_load_error);
            return icons
        },
        process_load_error: function (response) {
            Event.fire('load-error');
        }
    },
    data() {
        return {
            current_contract_id: window.CONTRACT_ID,
            clinic_id: window.CLINIC_ID,
            axios: require('axios')
        }
    }
})


Vue.use(vmodal, {componentName: 'Modal'})
Vue.use(VueConfirmDialog)
Vue.component('vue-confirm-dialog', VueConfirmDialog.default)

new Vue({
    el: '#app',
    render: h => h(App),
})
