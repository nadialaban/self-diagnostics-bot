<template>
  <div>
    <vue-confirm-dialog></vue-confirm-dialog>

    <loading v-if="state == 'loading'"/>

    <div v-else>
      <div v-if="mode == 'admin'">
        <div class="container" style="margin-top: 15px;">
          <settings-page v-if="state == 'settings'"></settings-page>
          <editor v-if="state == 'edit-algorithm' || state == 'create-algorithm'"
                  :data="info" :action="state"></editor>
        </div>
      </div>

      <div v-if="mode == 'patient'">
        <div class="container" style="margin-top: 15px;">
          <main-page v-if="state == 'main'"></main-page>
          <question v-if="state == 'test'" :data="info"></question>
          <result v-if="state == 'result'" :data="info"></result>
        </div>
      </div>

      <action-done v-if="state == 'done'"></action-done>
      <load-error v-if="state == 'load-error'"></load-error>

    </div>
  </div>
</template>

<script>

import Loading from "./components/Loading";
import ActionDone from "./components/ActionDone";
import LoadError from "./components/LoadError";
import MainPage from "./components/presenter/MainPage";
import Question from "./components/presenter/Question";
import Result from "./components/presenter/Result";
import SettingsPage from "./components/settings/SettingsPage";
import Editor from "./components/settings/Editor";


export default {
  name: 'app',
  components: {
    Editor,
    SettingsPage,
    Result,
    Question,
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
      info: {}
    }
  },
  created() {
    console.log("running created");

    Event.listen('start-test', (algorithm_id) => {
      this.state = 'loading'
      this.info = {
        'history': [],
        'algorithm_id': algorithm_id,
        'question_id': 1
      }
      this.state = 'test'
    });

    Event.listen('show-result', (data) => {
      this.state = 'loading'
      this.info = data
      this.state = 'result'
    });

    Event.listen('previous-question', (data) => {
      this.state = 'loading'

      let previous_answer = data.history.pop()
      this.info = {
        'history': data.history,
        'algorithm_id': previous_answer.algorithm_id,
        'question_id': previous_answer.question_id
      }

      this.state = 'test'
    });

    Event.listen('create-algorithm', () => {
      this.state = 'loading'
      this.info = this.get_empty_algorithm()
      this.state = 'create-algorithm'
    });

    Event.listen('edit-algorithm', (algorithm_id) => {
      this.state = 'loading'
      this.info = this.get_algorithm(algorithm_id)
      this.state = 'edit-algorithm'
    })

    Event.listen('back-to-menu', () => this.state = 'main');

    Event.listen('delete-algorithm', () => this.state = 'settings');
    Event.listen('back-to-settings', () => this.state = 'settings');

    Event.listen('algorithm-done', () => this.state = 'done');
    Event.listen('save-algorithm', () => this.state = 'done');
    Event.listen('settings-set', () => this.state = 'done');
  },
  methods: {
    load: function () {
      this.mode = window.MODE
      this.state = window.STATE
      this.recommended_algorithms = window.REC

      if (this.mode == 'admin') {
        this.state = 'settings'
      }
      if (this.mode == 'patient') {
        this.state = 'main'
      }
    },
    process_load_error: function (response) {
      this.state = 'load-error'
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

</style>

