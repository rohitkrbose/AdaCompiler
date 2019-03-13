procedure Fibonacci is
begin
   declare 
      function Fib (N: Integer) return Integer is
      begin
            return Fib( N - 1 ) + Fib( N - 2 );
      end Fib;
   i: Integer;
   begin
      i := 1;
      Ada.Text_IO.Put ("...");
   end;
end Fibonacci;
