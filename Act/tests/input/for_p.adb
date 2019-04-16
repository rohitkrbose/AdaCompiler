with Ada.Text_IO;
use Ada.Text_IO;

procedure for_p is
	procedure main is
		Count,k,u : Integer;
	begin
			Count := 6;
			Count := 5;
			for Count in 1 .. 5 loop
				for k in 6 .. 8 loop
					u := Count*k;
					print_int (u);
				end loop;
			end loop;
			k := Count + 6*k;
			-- print_int (Count);
	end ;
begin
	main;
end;