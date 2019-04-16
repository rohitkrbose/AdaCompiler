with Ada.Text_IO;
use Ada.Text_IO;

procedure arithmetic is
	x : integer;
	procedure main is
		k,i : integer;
		j,z : float;
	begin
		k := 5;
		z := k*2;
		j := 5.0;
		z := j*z + 2.3;
		print_float (z);
	end;
begin
	main;
end;