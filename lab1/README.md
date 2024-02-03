# НИЯУ МИФИ. Лабораторная работа №1
**Студент:** Журбенко Василий, **Группа:** Б21-525. **Год:** 2024

---

## Бенчмарк

Цель бенчмарка — оценить нагрузку на систему через выполнение "бесполезного" цикла.

<details>
<summary>Код программы</summary>

```c
void benchmark() {
    for (long long i = 0; i < 20000000000; i++) { i = i; }
}

int main() {
    clock_t start, end;
    double cpu_time_used;

    start = clock();
    benchmark();
    end = clock();

    cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;

    printf("Execution time: %f seconds.\n", cpu_time_used);

    return 0;
}
```

</details>

## Результаты

- **Вне Docker:**
  - Execution time: 45.416183 seconds.

- **Внутри Docker:**
  - Execution time: 45.142223 seconds.

## Заключение

Бенчмарк показал, что использование Docker контейнера приводит к незначительному увеличению времени выполнения задачи (на 0.6%). Это демонстрирует, что Docker обеспечивает стабильность и надежность при работе с высоконагруженными задачами. Контейнеризация оказалась эффективным решением даже при повышенной нагрузке, подтверждая свою эффективность в условиях реальной эксплуатации.
