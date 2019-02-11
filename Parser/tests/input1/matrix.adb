with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure Ch10_2 is

type MATRIX is array(1..3,1..5) of INTEGER;

First  : MATRIX := ((1, 1, 1, 1, 1),
                    (2, 2, 2, 2, 2),
                    (3, 3, 3, 3, 3));

Second : MATRIX := ((1, 2, 3, 4, 5),
                    (1, 2, 3, 4, 5),
                    (1, 2, 3, 4, 5));

Result : MATRIX;

begin
   for Index1 in 1 .. 3 loop
      for Index2 in 1 .. 5 loop
         Result(Index1, Index2) := First(Index1, Index2) *
                                   Second(Index1, Index2);
      end loop;
   end loop;

   for Index1 in 1..3 loop
      for Index2 in 1..5 loop
         Put(Result(Index1, Index2), 4);
      end loop;
      New_Line;
   end loop;
end Ch10_2;




-- Result of execution

--    1   2   3   4   5
--    2   4   6   8  10
--    3   6   9  12  15

