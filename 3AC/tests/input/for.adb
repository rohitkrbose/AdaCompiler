procedure LoopDemo is
   Count,k : Integer;

begin
   Count := 6;
   Count := 5;
   for Count in 1 .. 5 loop
      Count := Count + 1;
   end loop;
   k := Count + 6*k;
end ;
   