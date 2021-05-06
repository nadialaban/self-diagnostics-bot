<template>
  <div>
    <div class="row">
      <div class="text-center col-2">
        <img v-if="mode === 'patient'" width="35px"
             :src="this.img_url('teal',this.algorithm.icon)" alt="">
        <slot></slot>
      </div>

      <div class="col-10">
        <div class="btn-group d-flex" role="group">
          <input class="btn btn-block text-left" type="button" data-toggle="collapse" aria-expanded="false"
                 :class="mode === 'admin' ? 'btn-outline-secondary' : (this.recommended ? 'btn-info' : 'btn-outline-info')"
                 :value="this.algorithm.title" :data-target="'#collapse' + this.algorithm.id"
                 :aria-controls="'collapse' + this.algorithm.id">

          <button v-if="this.editable" type="button" class="btn btn-outline-secondary"
                  @click="fire_event('edit-test')" style="width: 50px;">
            <svg viewBox="0 0 16 16" class="bi bi-pencil-square" fill="currentColor"
                 xmlns="http://www.w3.org/2000/svg">
              <path
                  d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456l-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
              <path fill-rule="evenodd"
                    d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>
            </svg>
          </button>
        </div>

        <div class="collapse" :id="'collapse' + this.algorithm.id">
          <div class="card card-body text-justify  col-10 offset-2">
            {{ mode === 'patient' ? algorithm.patient_description : algorithm.doctor_description }}
            <button v-if="this.mode === 'patient'" class="btn btn-block btn-info"
                    @click="fire_event('start-test')"
                    style="margin-top: 15px; width: 200px;">Начать
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Card",
  props: ['algorithm', 'editable', 'recommended', 'mode'],
  methods: {
    fire_event: function (event) {
      Event.fire(event, this.algorithm.id)
    }
  }
}
</script>

<style scoped>
.row {
  margin-top: 10px;
}

.btn-group {
  border-radius: 5px 5px 0 0 !important;
}

.card {
  border-radius: 0 0 5px 5px !important;
}
</style>