with Ada.Text_IO, Ada.Integer_Text_IO;

procedure fibonacci is
   function Fib (N: integer) return integer is
      a,b : integer;
   begin
      if N < 3 then
         return 1;
      else 
         return Fib(N - 1) + Fib(N - 2);
      end if;
   end;
   procedure main is
      i: integer;
   begin
      i := Fib (8);
      print_int (i);
   end;
begin
   main;
end;
