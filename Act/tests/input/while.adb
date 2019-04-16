with Ada.Text_IO;
use Ada.Text_IO;

procedure While_L is
	procedure main is
		Count,k,Temperature : Integer;
		z : Float;
	begin
		Count := 1;
		while Count < 5 loop           
			k := Count * 5 + 8;
			Count := Count + 1;
			print_int (k);
		end loop;
		k := 7;
	end;
begin
	main;
end;