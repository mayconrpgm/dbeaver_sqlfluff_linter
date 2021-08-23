SELECT a+b AS foo,
c AS bar, 0 AS test, column, sum(qtd)
from my_table tba
join my_other_table tbb ON tbb.id = tba.id
group by 1, 2, 3, 4;