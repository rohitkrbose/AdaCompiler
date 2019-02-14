with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure Ch10_2 is

type MATRIX is array(1 .. 3, 1 .. 5) of INTEGER;

First  : MATRIX := ((1));

Result : MATRIX;

x : lambda a := a + 10 ;

begin
   for Index1 in 1 .. 3 loop
      for Index2 in 1 .. 5 loop
         Result(Index1, Index2) := First(Index1, Index2) *
                                   Second(Index1, Index2);
      end loop;
   end loop;

   

end Ch10_2;