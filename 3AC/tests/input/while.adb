procedure LoopDemo is

   Count,k,Temperature : Integer;

begin
   Count := 1;
   k := 6;
   if Temperature >= 40 then
   	if Temperature < 50 then
   		k := 4;
   		k := k*k;
   	end if;
   	else
   	while Count < 5 loop           
      Count := Count * 5;
   end loop;
   	k := 4+k;
   end if;
   k := 8;
end;
   