<template>
  <div class="container">
    <div class="btn-group d-flex">
      <button class="btn btn-block btn-outline-info"
              @click="fire_event('back-to-menu')">К началу
      </button>
      <button class="btn btn-block btn-outline-info"
              v-if="!history.empty()"
              @click="fire_event('previous-question')">Предыдущий вопрос
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "GoBackButtons",
  props: ['history'],
  methods: {
    fire_event: function (event) {
      if (this.history.empty()) {
        Event.fire('back-to-menu');
      } else if (event == 'back-to-menu') {
        this.$confirm({
          message: `Вы уверены? Ваши ответы будут утеряны!`,
          button: {
            no: 'Нет',
            yes: 'Да'
          },
          callback: confirm => {
            if (confirm) {
              Event.fire(event)
            }
          }
        })
      } else {
        let data = {'history': this.history}
        Event.fire(event, data);
      }
    }
  }
}
</script>

<style scoped>
.btn-group {
  margin-top: 15px;
}

</style>