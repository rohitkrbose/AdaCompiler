procedure Shit is
   Temperature, k : Integer;
begin
	k := 6;
   if Temperature >= 40*7 then
   	if Temperature < 50 then
   		k := 4;
   		k := k*k;
   	end if;
   else
   	k := 4+k;
   end if;
end ;