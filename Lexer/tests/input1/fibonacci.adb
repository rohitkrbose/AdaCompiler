with Ada.Text_IO, Ada.Integer_Text_IO;

procedure Fibonacci is
begin
   declare 
      function Fib (N: Integer) return Integer is
      begin
         if N < 3 then
            return 1;
         else 
            return Fib(N - 1) + Fib(N - 2);
         end if;
      end Fib;
   i: Integer := 1;
   begin
      loop
         Ada.Integer_Text_IO.Put (Item => Fib(i), Width => 1);
         Ada.Text_IO.Put (", ");
         i := i + 1;
         exit when i = 17;
      end loop;
      Ada.Text_IO.Put ("...");
   end;
end Fibonacci;
