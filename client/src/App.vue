<template>
  <article class="main-table">
    <section class="main-table__controls">
      <div class="input-group">
        <button type="button" class="btn btn-outline-secondary filter-column">
          {{ filterByColumn ? filterByColumn : 'Выбор колонки:' }}
        </button>
        <button type="button"
                class="btn btn-outline-secondary dropdown-toggle dropdown-toggle-split"
                data-bs-toggle="dropdown" aria-expanded="false">
          <span class="visually-hidden">Toggle Dropdown</span>
        </button>
        <ul class="dropdown-menu">
          <li v-for="(column, index) in filterTableColumns" :key="index">
            <a @click="filterByColumn=column" class="dropdown-item" href="#">{{ column }}</a>
          </li>
        </ul>
        <button type="button" class="btn btn-outline-secondary"
                v-html="filterOperand ? filterOperand : 'Выбор условия:'"
        ></button>
        <button type="button"
                class="btn btn-outline-secondary dropdown-toggle dropdown-toggle-split"
                data-bs-toggle="dropdown" aria-expanded="false">
          <span class="visually-hidden">Toggle Dropdown</span>
        </button>
        <ul class="dropdown-menu">
          <li v-for="(operand, index) in filterOperands" :key="index">
            <a @click="filterOperand=operand"
               v-html="operand"
               class="dropdown-item" href="#"
               aria-label="less"></a>
          </li>
        </ul>
        <input v-model="filterByValue" type="text" class="form-control"
               aria-label="Фильтрация таблицы">
        <button
            @click=makeFilterQuery()
            :disabled=isNotFilledFilter
            class="btn btn-outline-secondary" type="button">Фильтровать
        </button>
      </div>
      <div class="input-group d-flex justify-content-between input-group-text ">
        <div class="">
          {{ displayedFilter }}
        </div>
        <div v-if="loading" class="lds-ellipsis">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
        <button @click=resetFilter() class="btn btn-outline-danger " type="button">
          Сбросить
        </button>
      </div>
    </section>
    <section class="main-table__table mt-3">
      <div v-if=requestError class="alert alert-danger">{{ this.requestError }}</div>
      <table v-if=!requestError class="table table-primary table-bordered table-striped">
        <thead>
        <tr>
          <th scope="col">#</th>
          <th :class="{'table-active': activeColumn==='date'}"
              class="table__head" scope="col">
            <button @click="sortTable('date')"
                    class="bg-transparent border-0 w-100 h-100 btn-sorting" aria-label="Дата">
              Дата
            </button>
          </th>
          <th :class="sortingColumn('name')"
              class="table__head" scope="col">
            <button @click.prevent="sortTable('name')"
                    class="bg-transparent border-0 w-100 h-100 btn-sorting" aria-label="Название">
              Название
            </button>
          </th>
          <th :class="sortingColumn('count')"
              class="table__head" scope="col">
            <button @click="sortTable('count')"
                    class="bg-transparent border-0 w-100 h-100 btn-sorting" aria-label="Количество">
              Количество
            </button>
          </th>
          <th :class="sortingColumn('distance')"
              class="table__head" scope="col">
            <button @click="sortTable('distance')"
                    aria-label="Расстояние" class="bg-transparent border-0 w-100 h-100">
              Расстояние
            </button>
          </th>
        </tr>
        </thead>
        <tbody>
        <template v-if="tableData">
          <tr v-for="(row, index) in tableData" :key="index">
            <th scope="row">{{ index + 1 + perPage * (currentPage - 1) }}</th>
            <td :class="{'table-active': activeColumn==='date'}" @click="activeColumn='date'">
              {{ row.date }}
            </td>
            <td :class="{'table-active': activeColumn==='name'}" @click="activeColumn='name'">
              {{ row.name }}
            </td>
            <td :class="{'table-active': activeColumn==='count'}" @click="activeColumn='count'">
              {{ row.count }}
            </td>
            <td :class="{'table-active': activeColumn==='distance'}"
                @click="activeColumn='distance'">
              {{ row.distance }}
            </td>

          </tr>
        </template>
        </tbody>
      </table>
      <div v-if="tableData===[]" class="">
        Нет данных
      </div>
    </section>
    <section class="main-table__paginate">
      <nav v-if="prevPage || nextPage" aria-label="paginate">
        <ul class="pagination">
          <li class="page-item"
              :class="{disabled: !hasPrevPage}"
          >
            <button class="page-link"
                    tabindex="-1"
                    :aria-disabled=!hasPrevPage
                    @click.prevent="loadPage(currentPage=currentPage - 1)">Previous
            </button>
          </li>
          <li v-if="hasPrevPage" class="page-item">
            <button @click.prevent="loadPage(currentPage=currentPage -1)"
                    class="page-link">{{ currentPage - 1 }}
            </button>
          </li>
          <li class="page-item active" aria-current="page">
            <button class="page-link">{{ currentPage }}</button>
          </li>
          <li v-if="hasNextPage" class="page-item">
            <button
                @click.prevent="loadPage(currentPage=currentPage + 1)"
                class="page-link"> {{ currentPage + 1 }}
            </button>
          </li>
          <li class="page-item" :class="{disabled: !hasNextPage}">
            <button class="page-link"
                    :aria-disabled=!hasNextPage
                    @click.prevent="loadPage(currentPage=currentPage + 1)"
            >Next
            </button>
          </li>
        </ul>
      </nav>
    </section>
  </article>
</template>

<script>
import 'bootstrap';
import loadTable from '@/api';

export default {
  name: 'App',
  data() {
    return {
      filterByValue: '',
      filterByColumn: '',
      filterOperand: '',
      requestError: '',
      activeColumn: '',
      loading: false,
      filterQuery: {},
      currentPage: 1,
      prevPage: '',
      nextPage: '',
      sorting: {
        column: null,
        direction: true,
      },
      perPage: 10,
      filterTableColumns: ['Название', 'Количество', 'Расстояние', 'Дата'],
      filterOperands: ['равно', 'содержит', 'больше', 'меньше'],
      tableData: [],
    };
  },
  async created() {
    await this.loadPage(this.currentPage, this.filterQuery);
  },
  methods: {
    async loadPage(pageNum) {
      this.loading = true;
      const response = await loadTable(pageNum, this.filterQuery);
      this.loading = false;
      window.response = response;
      this.tableData = response.data;
      this.prevPage = response.prev;
      this.requestError = response.error;
      this.nextPage = response.next;
      this.currentPage = response.page;
    },
    async makeFilterQuery() {
      this.filterQuery = {
        column: this.filterByColumn,
        operand: this.filterOperand,
        value: this.filterByValue,
      };
      // this.blankAllFiltres();
      await this.loadPage(1);
    },
    async resetFilter() {
      this.blankAllFiltres();
      await this.makeFilterQuery();
    },
    blankAllFiltres() {
      this.filterByColumn = '';
      this.filterOperand = '';
      this.filterByValue = '';
    },
    sortingColumn(column) {
      let style = this.activeColumn === column ? 'table-active ' : '';
      if (this.sorting.column === column) {
        style += this.sorting.direction ? 'head_sorted-up' : 'head_sorted-down';
      }
      return style;
    },
    sortTable(column) {
      this.activeColumn = column;
      this.sorting.column = column;
      if (column !== 'name') {
        if (this.sorting.direction) {
          this.tableData.sort((a, b) => a[column] - b[column]);
        } else {
          this.tableData.sort((a, b) => b[column] - a[column]);
        }
      } else if (this.sorting.direction) {
        this.tableData.sort((a, b) => a[column].localeCompare(b[column]));
      } else {
        this.tableData.sort((a, b) => b[column].localeCompare(a[column]));
      }
      this.sorting.direction = !this.sorting.direction;
    },
  },
  computed: {
    isNotFilledFilter() {
      const filterValues = [this.filterOperand, this.filterByColumn, this.filterByValue];
      return !filterValues.every((value) => value !== '');
    },
    displayedFilter() {
      return `${this.filterByColumn} ${this.filterOperand} ${this.filterByValue}`;
    },
    isTableDataLoad() {
      return this.tableData !== [];
    },
    hasNextPage() {
      return this.nextPage !== '';
    },
    hasPrevPage() {
      return this.prevPage !== '';
    },
    checked_name() {
      return this.filterByColumn === 'Название';
    },
    checked_contain() {
      return this.filterOperand === 'содержит';
    },
  },
  watch: {
    filterByColumn(column) {
      if (column !== 'Название') {
        this.filterOperands = ['равно', 'больше', 'меньше'];
        if (this.filterOperand === 'содержит') {
          this.filterOperand = '';
        }
      } else {
        this.filterOperands = ['равно', 'содержит'];
      }
    },
    filterOperand(operand) {
      if (operand === 'содержит') {
        this.filterTableColumns = ['Название'];
        if (this.filterByColumn !== 'Название') {
          this.filterByColumn = '';
        }
      } else {
        this.filterTableColumns = ['Название', 'Количество', 'Расстояние', 'Дата'];
      }
    },
  },
};
</script>

<style lang="scss">
@import "~bootstrap/scss/bootstrap";

body {
  padding: 0;
  margin: 0;
  border: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100vh;
  display: grid;
  grid-template: 4vh 1fr 4vh / 5vw 90vw 5vw;

}

.main-table {
  grid-row: 2;
  grid-column: 2;
  display: grid;
  grid-template-areas:
    "controls"
    "tables"
    "paginate";
  grid-template-rows: 75px auto 40px;

  &__controls {
    grid-area: controls;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
  }

  &__table {
    grid-area: tables;
  }

  &__paginate {
    grid-area: paginate;
    display: grid;
    align-items: center;
    justify-items: center;
  }
}

.table__head {
  cursor: pointer;

  &.head_sorted-down {
    position: relative;

    &::after {
      content: "\25B3";
      position: absolute;
      right: 15px;
      pointer-events: none;
    }
  }

  &.head_sorted-up {
    position: relative;

    &::after {
      content: "\25BD";
      position: absolute;
      right: 15px;
      pointer-events: none;;
    }
  }
}

.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}

.lds-ellipsis div {
  position: absolute;
  top: 33px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #fff;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}

.lds-ellipsis div:nth-child(1) {
  left: 8px;
  animation: lds-ellipsis1 0.6s infinite;
}

.lds-ellipsis div:nth-child(2) {
  left: 8px;
  animation: lds-ellipsis2 0.6s infinite;
}

.lds-ellipsis div:nth-child(3) {
  left: 32px;
  animation: lds-ellipsis2 0.6s infinite;
}

.lds-ellipsis div:nth-child(4) {
  left: 56px;
  animation: lds-ellipsis3 0.6s infinite;
}

@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}

@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(24px, 0);
  }
}

</style>
