<template>
  <div class="container">
    <vue-confirm-dialog></vue-confirm-dialog>

    <loading v-if="state == 'loading'"/>

    <div v-else>
      <div v-if="mode == 'admin'">
        <div class="container" style="margin-top: 15px;">
          <settings-page v-if="state == 'settings'"
                         :algorithms="algorithms"
                         :enabled="info"></settings-page>
          <editor v-if="state == 'edit-algorithm' || state == 'create-algorithm'"
                  :algorithms="algorithms" :icons="icons"
                  :data="info" :action="state"></editor>
        </div>
      </div>

      <div v-else-if="mode == 'patient'">
        <div class="container" style="margin-top: 15px;">
          <main-page v-if="state == 'main'" :mode="mode"
                     :algorithms="algorithms"
                     :recommended="recommended_algorithms"></main-page>
          <test v-if="state == 'test'" :data="info"></test>
          <result v-if="state == 'result'" :data="info"></result>
        </div>
      </div>

      <action-done v-if="state == 'done'"></action-done>
      <load-error v-if="state == 'load-error'"></load-error>

      <br>
      <br>

    </div>
  </div>
</template>

<script>

import Loading from "./components/Loading";
import ActionDone from "./components/ActionDone";
import LoadError from "./components/LoadError";
import MainPage from "./components/presenter/MainPage";
import Test from "./components/presenter/Test";
import SettingsPage from "./components/settings/SettingsPage";
import Editor from "./components/settings/Editor";
import Result from "./components/presenter/Result";


export default {
  name: 'app',
  components: {
    Result,
    Editor,
    SettingsPage,
    Test,
    MainPage,
    LoadError,
    ActionDone,
    Loading
  },
  data() {
    return {
      mode: "",
      state: "loading",
      recommended_algorithms: [],
      enabled_algorithms: [],
      algorithms: [],
      current_algorithm: {},
      icons: {},
      info: {},
      response: null
    }
  },
  created() {
    console.log("running created");
    this.axios.get(this.url('/api/icons')).then(response => this.icons = response.data);

    Event.listen('start-test', (algorithm_id) => {
      this.state = 'loading'
      this.info = {
        'history': [],
        'algorithm': {},
        'question_id': 1
      }
      this.axios.get(this.url('/api/algorithm/' + algorithm_id))
          .then(response => this.info.algorithm = response.data)
          .catch(this.process_load_error)
          .finally(() => this.state = 'test');
    });

    Event.listen('show-result', (data) => {
      this.state = 'loading'
      this.info = data
      this.state = 'result'
    });

    Event.listen('back-to-test', (data) => {
      this.state = 'loading'
      let previous_answer = data.history.pop()
      this.info = {
        'history': data.history,
        'algorithm': data.algorithm,
        'question_id': previous_answer.question_id
      }
      console.log(data)
      this.state = 'test'
    });

    Event.listen('create-algorithm', () => {
      this.state = 'loading'
      this.info = this.get_empty_algorithm()
      this.state = 'create-algorithm'
    });

    Event.listen('edit-algorithm', (algorithm_id) => {
      this.state = 'loading'
      let index = this.algorithms.map(alg => alg.id).indexOf(algorithm_id)
      this.algorithms.splice(index, 1)
      this.axios.get(this.url('/api/algorithm/' + algorithm_id))
          .then(response => this.info = response.data)
          .catch(this.process_load_error)
          .finally(() => this.state = 'edit-algorithm');
    });

    Event.listen('delete-algorithm', () => this.state = 'settings');

    Event.listen('back-to-settings', () => this.load_settings());
    Event.listen('back-to-menu', () => this.load_main_page());

    Event.listen('algorithm-done', () => this.state = 'done');
    Event.listen('save-algorithm', () => this.state = 'done');
    Event.listen('settings-set', () => this.state = 'done');
    this.load()
  },
  methods: {
    load: function () {
      this.mode = window.MODE
      this.recommended_algorithms = window.REC ? window.REC.split('_') : []

      if (this.mode == 'admin') {
        this.load_settings()
      }
      if (this.mode == 'patient') {
        this.load_main_page()
      }
    },
    process_load_error: function (response) {
      Event.fire('load-error');
    },
    load_settings: function () {
      this.axios.get(this.url('/api/algorithms'))
          .then(response => {
            this.algorithms = response.data.algorithms
            this.info = response.data.enabled
          })
          .catch(this.process_load_error)
          .finally(() => {
            this.state = 'settings'
          });
    },
    load_main_page: function () {
      let link = window.REC ? '/api/enabled_algorithms/' + window.REC : '/api/enabled_algorithms'
      this.axios.get(this.url(link))
          .then(response => {
            this.algorithms = response.data.algorithms
          })
          .catch(this.process_load_error)
          .finally(() => {
            this.state = 'main'
          });
    }
  },
  mounted: function () {
    this.load();
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

a {
  color: #42b983;
}

body {
  background-color: #f8f8fb;
}

.card-body {
  background-color: #f8f8fb;
}

.container {
  margin-top: 15px;
}
</style>

